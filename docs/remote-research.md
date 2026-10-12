# PGST Remote and Panel Protocol Investigation

The Tuya-local event entity exposes DP26 zone messages; our currently observed remote SOS payload is `SOS from Remote / Zone:000`. Alarm panel state reports arm/disarm but **does not identify the actor or remote**. Do not infer remote identity from a panel transition.

## Possible additional surfaces (not yet verified)

1. **Local Tuya datapoints** beyond DP26. Inspect the device's reported DP schema / debug-level tuya-local logs for DP36/37/39, arm/disarm command acknowledgements, and any separate accessory event payloads. The present device YAML already defines optional DP37 (`sub_type`) and DP39 (`sub_state`), but those attributes were absent from tested event snapshots. Their presence in a definition is **not evidence of actual data**.
2. **Tuya cloud device status/event history** through officially supported diagnostic APIs, if available and authorized. Cloud records might include action provenance but may only duplicate panel mode/status.
3. **Panel-local RF receiver**: hardware UART/debug telemetry, serial-to-Wi-Fi bridge, or a separate 433 MHz receive-only SDR / ESPHome-compatible receiver, if remote packet-level differentiation is desired. That is a distinct hardware research project, and identity/rolling-code security cannot be assumed.
4. **Tuya-local raw inbound packets**: capture sanitized DP IDs/types and redacted payload shape from debug logs during controlled actions. Do not log credentials, device local keys, tokens, or raw authentication material in issue reports.

## Controlled test matrix

For each of the three remotes, compare `arm`, `disarm`, and `SOS` actions. Separately compare keypad, Smart Life app, and RFID fobs if interested. Record the current panel mode, whether a DP26 event occurs, which optional DP IDs change, and whether the event occurs when transitioning from armed, triggered, or disarmed.

**Important:** The panel can enter triggered state from 24-hour-silent zones and may later be disarmed simply to reset the alarm. Such a disarm must never be interpreted as an arrival or user authentication.

## Access control

The proposed integration does **not** expose a door-unlock service or automatically unlock any door. If a separate radio receiver later reveals stable identifiers, verify remote authentication/replay resistance and avoid using an unauthenticated fixed-code RF button as sole authority for unlocking a residential entry. Presence or a short time window alone does not authenticate the person operating the remote.

## Development

Focus near-term implementation on reliable zone state handling, tests, diagnostics, and avoiding loss of configuration. Keep the panel observer strictly read-only.