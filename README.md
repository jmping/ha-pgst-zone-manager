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
