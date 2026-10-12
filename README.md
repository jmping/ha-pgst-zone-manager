# PGST Zone Manager (experimental)

Home Assistant custom integration that interprets an existing PGST alarm-panel event entity (such as `event.multifunction_alarm_alarm`) as zone-based motion, contact activity, and button entities. No direct Tuya connection or panel arming commands.

**Prototype; not yet tested against a running Home Assistant instance.** Do not use as a security or emergency-alert system.

## Installation

Copy `custom_components/pgst_zone_manager` into your Home Assistant `/config/custom_components/`, restart, then add **PGST Zone Manager** from Settings → Devices & services. Choose the PGST event entity. Configure zones through the integration's Configure dialog (JSON text editor for now).

The four working window zones **008, 009, 010, 012 are disabled by default** to avoid disrupting existing helpers/automations. Motion zones 001–005 are timed binary sensors; door contacts 006, 007, 011, 013–015 are *recent activity*, not actual open/closed states. Zone 000 is remote SOS; zone 016 is the panic button. The parser uses the `Zone:NNN` identifier, not Smart Life accessory numbering.

## Limitations

- UI configuration currently uses validated JSON, not individual per-zone controls.
- Window toggle mode is experimental; existing window helpers remain authoritative. Binary sensors are read-only in normal Home Assistant UI, so manual correction needs a dedicated service/helper before migration.
- Event counts reset on restart; timed sensors do not imply confirmed occupancy.
- Panel events cannot identify individual remotes from the observed payloads.
- A missed RF event can leave an inferred window state incorrect.

MIT licensed. See LICENSE.

## Development branch: v0.2.0

The proposed update replaces the raw JSON options editor with a per-zone Home Assistant form (choose a zone, edit its name, mode, enable flag, timeout, and contact type). It records the last activity timestamp and per-entity event count. A new `pgst_zone_manager.set_window_state` service accepts `zone` (integer) and `is_open` (boolean) to correct an inferred toggle-window state without generating a fake PGST event. The default window zones remain disabled; leave existing window tracking in place until tested. These changes are in a draft pull request and are not part of the HACS main-branch download yet.

## Panel mode observation / remote experiments

Optional **Panel state observation** in the Configure flow selects `alarm_control_panel.multifunction_alarm`. The new **PGST Panel Last Transition** diagnostic sensor records genuine changes (such as armed → disarmed), including previous/current state and timestamp. This is read-only, performs **no lock actions**, and does **not establish which remote** caused a disarm. All three observed remotes currently appear indistinguishable in the DP26 message `SOS from Remote / Zone:000`; the alarm mode may also change by app, keypad, RFID, or automation. Investigate whether independent remote identifiers or authenticated keypad/user codes can be surfaced before considering access-control automation. Do **not** link a raw disarm transition directly to a front-door unlock. An alarm transition is not an authenticated unlock credential. Also beware that 24-hour silent sensors can trigger alarming even when disarmed, so a later disarm may just be an alarm reset, not an arriving family member.
