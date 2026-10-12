"""Read-only PGST diagnostics."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([
        DiagnosticSensor(entry.entry_id, key, name)
        for key, name in (
            ("last_zone", "PGST Last Zone"),
            ("last_message", "PGST Last Message"),
            ("seen", "PGST Events Received"),
            ("unknown", "PGST Unknown Events"),
        )
    ])


class DiagnosticSensor(SensorEntity):
    _attr_should_poll = False
    _attr_entity_category = "diagnostic"

    def __init__(self, entry_id, key, name):
        self.entry_id, self.key = entry_id, key
        self._attr_name = name
        self._attr_unique_id = f"{entry_id}_diag_{key}"

    @property
    def native_value(self):
        return self.hass.data[DOMAIN][self.entry_id][self.key]

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.entry_id}_diagnostic", self._update
        ))

    @callback
    def _update(self):
        self.async_write_ha_state()
