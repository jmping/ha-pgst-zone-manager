"""Momentary PGST button events."""
from homeassistant.components.event import EventEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import CONF_ZONES, DEFAULT_ZONES, DOMAIN, MODE_BUTTON


async def async_setup_entry(hass, entry, async_add_entities):
    zones = entry.options.get(CONF_ZONES, DEFAULT_ZONES)
    async_add_entities([
        ZoneButtonEvent(entry.entry_id, zone, config)
        for zone, config in zones.items()
        if config.get("enabled", True) and config["mode"] == MODE_BUTTON
    ])


class ZoneButtonEvent(EventEntity):
    _attr_should_poll = False
    _attr_event_types = ["press"]

    def __init__(self, entry_id, zone, config):
        self.entry_id, self.zone = entry_id, zone
        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry_id}_zone_{zone}_button"
        self._attr_extra_state_attributes = {"pgst_zone": zone}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.entry_id}_event", self._on_event
        ))

    @callback
    def _on_event(self, zone, message):
        if zone == self.zone:
            self._trigger_event("press", {"message": message or ""})
            self.async_write_ha_state()
