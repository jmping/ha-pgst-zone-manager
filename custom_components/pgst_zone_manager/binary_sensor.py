"""Motion, activity, and estimated contact entities."""
from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.components.binary_sensor import BinarySensorDeviceClass, BinarySensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.restore_state import RestoreEntity

from .const import CONF_ZONES, DEFAULT_ZONES, DOMAIN, MODE_MOTION, MODE_ACTIVITY, MODE_TOGGLE


async def async_setup_entry(hass, entry, async_add_entities):
    zones = entry.options.get(CONF_ZONES, DEFAULT_ZONES)
    async_add_entities([
        ZoneBinarySensor(entry.entry_id, zone, config)
        for zone, config in zones.items()
        if config.get("enabled", True) and config["mode"] in
        (MODE_MOTION, MODE_ACTIVITY, MODE_TOGGLE)
    ])


class ZoneBinarySensor(RestoreEntity, BinarySensorEntity):
    """Recent activity or persistent inferred contact state."""
    _attr_should_poll = False

    def __init__(self, entry_id, zone, config):
        self.entry_id, self.zone, self.config = entry_id, zone, config
        self._attr_name = config["name"]
        self._attr_unique_id = f"{entry_id}_zone_{zone}"
        mode = config["mode"]
        kind = config.get("device_class", "window") if mode == MODE_TOGGLE else (
            "motion" if mode == MODE_MOTION else "opening"
        )
        self._attr_device_class = BinarySensorDeviceClass(kind)
        initial = config.get("initial_state", "unknown")
        self._attr_is_on = (initial == "open") if mode == MODE_TOGGLE and initial != "unknown" else (
            None if mode == MODE_TOGGLE else False
        )
        self._reset = None
        self._last_activity = None
        self._event_count = 0

    @property
    def extra_state_attributes(self):
        return {
            "pgst_zone": self.zone,
            "mode": self.config["mode"],
            "last_activity": self._last_activity,
            "event_count": self._event_count,
            "state_is_estimated": self.config["mode"] == MODE_TOGGLE,
        }

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        previous = await self.async_get_last_state()
        if previous:
            self._last_activity = previous.attributes.get("last_activity")
            try:
                self._event_count = int(previous.attributes.get("event_count", 0))
            except (ValueError, TypeError):
                self._event_count = 0
            if self.config["mode"] == MODE_TOGGLE and self.config.get("initial_state", "unknown") == "unknown":
                if previous.state in ("on", "off"):
                    self._attr_is_on = previous.state == "on"
        self.async_on_remove(async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.entry_id}_event", self._on_event
        ))
        self.async_on_remove(self._cancel_reset)

    @callback
    def _cancel_reset(self):
        if self._reset is not None:
            self._reset()
            self._reset = None

    @callback
    def _clear(self, _now):
        self._reset = None
        self._attr_is_on = False
        self.async_write_ha_state()

    @callback
    def _on_event(self, zone, message):
        if zone != self.zone:
            return
        self._last_activity = datetime.now(timezone.utc).isoformat()
        self._event_count += 1
        if self.config["mode"] == MODE_TOGGLE:
            if self._attr_is_on is None:
                # Preserve unknown until calibrated; still record activity.
                self.async_write_ha_state()
                return
            self._attr_is_on = not self._attr_is_on
        else:
            self._attr_is_on = True
            self._cancel_reset()
            self._reset = async_call_later(
                self.hass, self.config.get("timeout", 120), self._clear
            )
        self.async_write_ha_state()
