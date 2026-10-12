"""UI configuration for PGST Zone Manager."""
import json

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import CONF_SOURCE, CONF_ZONES, DEFAULT_ZONES, DOMAIN, MODES


def validate_zones(raw: str) -> dict:
    """Validate editable zone configuration JSON."""
    zones = json.loads(raw)
    if not isinstance(zones, dict):
        raise ValueError("Zones must be a JSON object")
    validated = {}
    for key, config in zones.items():
        if not isinstance(key, str) or not key.isdigit() or not 0 <= int(key) <= 255:
            raise ValueError(f"Invalid zone number: {key}")
        if not isinstance(config, dict) or config.get("mode") not in MODES:
            raise ValueError(f"Invalid mode for zone {key}")
        name = config.get("name", f"Zone {int(key):03d}")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Invalid name for zone {key}")
        timeout = config.get("timeout", 120)
        if not isinstance(timeout, int) or not 1 <= timeout <= 86400:
            raise ValueError(f"Invalid timeout for zone {key}")
        kind = config.get("device_class", "window")
        if kind not in ("window", "door", "opening"):
            raise ValueError(f"Invalid device class for zone {key}")
        enabled = config.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"Invalid enabled value for zone {key}")
        normalized = dict(config)
        normalized.update(name=name.strip(), timeout=timeout, device_class=kind, enabled=enabled)
        canonical = f"{int(key):03d}"
        if canonical in validated:
            raise ValueError(f"Duplicate zone {canonical}")
        validated[canonical] = normalized
    return validated


class PGSTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Set the source event entity."""
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            source = user_input[CONF_SOURCE]
            await self.async_set_unique_id(source)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title="PGST Zone Manager",
                data={CONF_SOURCE: source},
                options={CONF_ZONES: DEFAULT_ZONES},
            )
        schema = vol.Schema({
            vol.Required(CONF_SOURCE): selector.EntitySelector(
                selector.EntitySelectorConfig(domain="event")
            )
        })
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    def async_get_options_flow(config_entry):
        return PGSTOptionsFlow()


class PGSTOptionsFlow(config_entries.OptionsFlow):
    """Edit mappings via the HA UI (validated JSON text field)."""

    async def async_step_init(self, user_input=None):
        errors = {}
        zones = self.config_entry.options.get(CONF_ZONES, DEFAULT_ZONES)
        if user_input is not None:
            try:
                new_zones = validate_zones(user_input[CONF_ZONES])
            except (ValueError, TypeError, json.JSONDecodeError):
                errors["base"] = "invalid_zones"
            else:
                return self.async_create_entry(title="", data={CONF_ZONES: new_zones})
        schema = vol.Schema({
            vol.Required(CONF_ZONES, default=json.dumps(zones, indent=2)):
                selector.TextSelector(selector.TextSelectorConfig(multiline=True))
        })
        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
