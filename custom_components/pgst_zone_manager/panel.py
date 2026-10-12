"""Observe panel arm/disarm transitions without operating the alarm or any lock.

Only a state transition of the configured alarm_control_panel entity is authoritative
for a panel-mode event. Tuya DP26 zone messages are not evidence of disarming.
"""
from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import callback
from homeassistant.helpers.dispatcher import async_dispatcher_send


VALID_ARMED = {"armed_away", "armed_home", "armed_night", "armed_vacation", "armed_custom_bypass"}
VALID_STATES = VALID_ARMED | {"disarmed", "pending", "arming", "triggered"}


def classify_transition(before: str | None, after: str | None) -> str | None:
    """Return a meaningful observed transition, or None for startup/duplicates."""
    if before not in VALID_STATES or after not in VALID_STATES or before == after:
        return None
    if after == "disarmed":
        return "disarmed"
    if after in VALID_ARMED:
        return "armed"
    if after == "triggered":
        return "triggered"
    return "mode_changed"


class PanelObserver:
    """Read-only view of an alarm panel and its last valid mode transition."""

    def __init__(self, hass, entry_id: str, entity_id: str):
        self.hass = hass
        self.entry_id = entry_id
        self.entity_id = entity_id
        self.last_transition = None
        self.last_transition_at = None
        self.previous_mode = None
        self.current_mode = None

    @callback
    def on_change(self, event):
        if event.data.get("entity_id") != self.entity_id:
            return
        old = event.data.get("old_state")
        new = event.data.get("new_state")
        if old is None or new is None:
            return
        transition = classify_transition(old.state, new.state)
        if transition is None:
            return
        self.previous_mode = old.state
        self.current_mode = new.state
        self.last_transition = transition
        self.last_transition_at = datetime.now(timezone.utc).isoformat()
        async_dispatcher_send(self.hass, f"pgst_zone_manager_{self.entry_id}_panel")

    @property
    def attributes(self):
        return {
            "observed_alarm_entity": self.entity_id,
            "previous_mode": self.previous_mode,
            "current_mode": self.current_mode,
            "last_transition_at": self.last_transition_at,
            "actor_identified": False,
            "credential_verified": False,
        }
