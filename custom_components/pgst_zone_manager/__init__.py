"""PGST Zone Manager: derive HA entities from a shared PGST event entity."""
from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import CONF_SOURCE, CONF_ZONES, DEFAULT_ZONES, DOMAIN
from .parser import parse_zone

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["binary_sensor", "event", "sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    source = entry.data[CONF_SOURCE]
    zones = entry.options.get(CONF_ZONES, DEFAULT_ZONES)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "source": source, "zones": zones, "seen": 0, "unknown": 0,
        "last_zone": None, "last_message": None,
    }

    @callback
    def handle_change(event):
        if event.data.get("entity_id") != source:
            return
        old = event.data.get("old_state")
        new = event.data.get("new_state")
        if new is None or new.state in ("unknown", "unavailable"):
            return
        # HA event entities use a timestamp as their state.
        # Do not replay restoration or attribute-only updates.
        if old is None or old.state in ("unknown", "unavailable") or old.state == new.state:
            return
        message = new.attributes.get("message")
        zone = parse_zone(message)
        data = hass.data[DOMAIN][entry.entry_id]
        data["seen"] += 1
        data["last_message"] = message
        data["last_zone"] = zone
        if zone is None or zone not in zones:
            data["unknown"] += 1
        async_dispatcher_send(hass, f"{DOMAIN}_{entry.entry_id}_event", zone, message)
        async_dispatcher_send(hass, f"{DOMAIN}_{entry.entry_id}_diagnostic")

    unsub = hass.bus.async_listen(EVENT_STATE_CHANGED, handle_change)
    hass.data[DOMAIN][entry.entry_id]["unsub"] = unsub
    entry.async_on_unload(entry.add_update_listener(_reload_entry))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _reload_entry(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        data = hass.data[DOMAIN].pop(entry.entry_id)
        data["unsub"]()
    return ok
