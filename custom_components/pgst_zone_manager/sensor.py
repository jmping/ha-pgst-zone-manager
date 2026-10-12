"""Read-only PGST diagnostics."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    entities = [PanelTransitionSensor(entry.entry_id)] if entry.options.get("panel_entity") else []
    entities += [
        DiagnosticSensor(entry.entry_id, key, name)
        for key, name in (
            ("last_zone", "PGST Last Zone"),
            ("last_message", "PGST Last Message"),
            ("seen", "PGST Events Received"),
            ("unknown", "PGST Unknown Events"),
        )
    ]
    async_add_entities(entities)


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


class PanelTransitionSensor(SensorEntity):
    """Read-only last observed panel mode transition; not an identity claim."""
    _attr_should_poll = False
    _attr_entity_category = "diagnostic"
    _attr_name = "PGST Panel Last Transition"

    def __init__(self, entry_id):
        self.entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_panel_transition"

    @property
    def native_value(self):
        observer = self.hass.data[DOMAIN][self.entry_id].get("panel_observer")
        return observer.last_transition if observer else None

    @property
    def extra_state_attributes(self):
        observer = self.hass.data[DOMAIN][self.entry_id].get("panel_observer")
        return observer.attributes if observer else {}

    async def async_added_to_hass(self):
        await super().async_added_to_hass()
        self.async_on_remove(async_dispatcher_connect(
            self.hass, f"{DOMAIN}_{self.entry_id}_panel", self._update
        ))

    @callback
    def _update(self):
        self.async_write_ha_state()
