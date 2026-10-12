"""UI configuration for PGST Zone Manager."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_SOURCE, CONF_ZONES, DEFAULT_ZONES, DOMAIN, MODES,
    MODE_ACTIVITY, MODE_BUTTON, MODE_DISABLED, MODE_MOTION, MODE_TOGGLE,
)

CONF_ZONE = "zone"
CONF_NAME = "name"
CONF_MODE = "mode"
CONF_ENABLED = "enabled"
CONF_TIMEOUT = "timeout"
CONF_DEVICE_CLASS = "device_class"
CONF_INITIAL = "initial_state"
CONF_PANEL = "panel_entity"


def zone_schema(existing: dict) -> vol.Schema:
    """Create native HA form controls for one zone."""
    mode = existing.get(CONF_MODE, MODE_DISABLED)
    return vol.Schema({
        vol.Required(CONF_NAME, default=existing.get(CONF_NAME, "New Zone")):
            selector.TextSelector(),
        vol.Required(CONF_MODE, default=mode):
            selector.SelectSelector(selector.SelectSelectorConfig(
                options=MODES, mode=selector.SelectSelectorMode.DROPDOWN,
            )),
        vol.Required(CONF_ENABLED, default=existing.get(CONF_ENABLED, True)):
            selector.BooleanSelector(),
        vol.Required(CONF_TIMEOUT, default=existing.get(CONF_TIMEOUT, 120)):
            vol.All(vol.Coerce(int), vol.Range(min=1, max=86400)),
        vol.Required(CONF_DEVICE_CLASS, default=existing.get(CONF_DEVICE_CLASS, "window")):
            selector.SelectSelector(selector.SelectSelectorConfig(
                options=["window", "door", "opening"],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )),
        vol.Optional(CONF_INITIAL, default=existing.get(CONF_INITIAL, "unknown")):
            selector.SelectSelector(selector.SelectSelectorConfig(
                options=["unknown", "open", "closed"],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )),
    })


class PGSTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set the source event entity."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            source = user_input[CONF_SOURCE]
            await self.async_set_unique_id(source)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="PGST Zone Manager",
                data={CONF_SOURCE: source},
                options={CONF_ZONES: DEFAULT_ZONES},
            )
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_SOURCE): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="event")
                )
            }),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return PGSTOptionsFlow()


class PGSTOptionsFlow(config_entries.OptionsFlow):
    """Select a zone and configure it without editing JSON."""

    async def async_step_init(self, user_input=None):
        self._zones = {
            key: dict(value) for key, value in
            self.config_entry.options.get(CONF_ZONES, DEFAULT_ZONES).items()
        }
        if user_input is not None:
            if user_input[CONF_ZONE] == "panel":
                return await self.async_step_panel()
            self._selected_zone = user_input[CONF_ZONE]
            return await self.async_step_edit()
        options = [
            selector.SelectOptionDict(value=key, label=f"{key} — {config.get('name', 'Zone')}")
            for key, config in sorted(self._zones.items())
        ]
        options.append(selector.SelectOptionDict(value="new", label="Add new zone"))
        options.append(selector.SelectOptionDict(value="panel", label="Panel state observation"))
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_ZONE): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=options, mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                )
            }),
        )

    async def async_step_edit(self, user_input=None):
        zone = self._selected_zone
        if zone == "new":
            return await self.async_step_add()
        if user_input is not None:
            self._zones[zone] = dict(user_input)
            return self.async_create_entry(
                title="", data={**self.config_entry.options, CONF_ZONES: self._zones}
            )
        return self.async_show_form(
            step_id="edit", data_schema=zone_schema(self._zones[zone]),
            description_placeholders={"zone": zone},
        )

    async def async_step_add(self, user_input=None):
        errors = {}
        if user_input is not None:
            zone = f"{int(user_input[CONF_ZONE]):03d}"
            if zone in self._zones:
                errors["base"] = "zone_exists"
            else:
                self._selected_zone = zone
                self._zones[zone] = {
                    "name": f"Zone {zone}", "mode": MODE_DISABLED, "enabled": False
                }
                return await self.async_step_edit()
        return self.async_show_form(
            step_id="add",
            data_schema=vol.Schema({
                vol.Required(CONF_ZONE): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=255)
                )
            }),
            errors=errors,
        )

    async def async_step_panel(self, user_input=None):
        """Configure optional observation of alarm arm/disarm state."""
        if user_input is not None:
            return self.async_create_entry(title="", data={
                **self.config_entry.options, CONF_PANEL: user_input.get(CONF_PANEL),
            })
        existing = self.config_entry.options.get(CONF_PANEL)
        schema = vol.Schema({
            vol.Optional(CONF_PANEL, default=existing) if existing else vol.Optional(CONF_PANEL):
                selector.EntitySelector(selector.EntitySelectorConfig(domain="alarm_control_panel"))
        })
        return self.async_show_form(step_id="panel", data_schema=schema)
