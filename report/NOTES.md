# Lab 2 Report Notes

Copy/adapt these into your official lab report. Keep them brief.

## Background — protocols for a real self-driving car platform (~1 paragraph)

A production AV fleet would use **several** wireless technologies together, chosen by range and bandwidth (see the lab’s range/bandwidth chart). **BLE** is a good fit for the driver’s phone (unlock, start, short diagnostics) because it is low power and short range. **Wi‑Fi (802.11)** works well in the garage or shop for high-bandwidth tasks such as camera log upload and firmware staging. Over the road, cars need wide coverage, so **4G/5G cellular** (and sometimes satellite for sparse areas) carries telemetry, maps, and OTA updates through existing carrier infrastructure. Crash-avoidance and “see around corners” style coordination may use dedicated **V2X / DSRC or C-V2X** links when standardized and available; until then fleets often fall back to low-latency cellular plus cloud mediation. RFID/NFC can still cover key-card unlock at the door. In short: short-range low-power for the user, high-bandwidth local for the shop, and cellular/cloud for continental operation—not a single protocol.

## Step 2 — WiFi web service (design)

- Pi runs a TCP server on port **65432** (`wifi_server.py`), bound to `0.0.0.0` so any LAN client can connect.
- One command per short-lived connection (matches the Electron starter pattern): easy to reason about, no sticky sessions.
- Response is always a **JSON status line** (≥3 fields: battery, temp, distance; also speed / moving / turning).
- Motors use Freenove `Ordinary_Car` with short timed PWM bursts so a single UI keypress moves then stops safely.
- `--dry-run` lets us test networking without spinning wheels.

## Step 3 — Electron frontend (design)

- Desktop app via Electron: HTML for layout, `index.js` for WASD/arrows + `require('net')` TCP client.
- Status polled every **500 ms** (not 50 ms) to avoid flooding the Pi while still feeling live.
- Same command vocabulary as the Python `wifi_client.py`, so either tool can drive the car.

## Step 1 — Bluetooth (bonus, deferred)

- PC RFCOMM sockets path (lab Section 4), not Flutter.
- Reuses `CarController` / JSON protocol from the WiFi server so control logic is not duplicated.

## Challenges

- Electron renderer needs `nodeIntegration` + `contextIsolation: false` for `net` sockets (lab note).
- Battery % is approximate from ADC voltage; if ADC init fails we still send other stats (`battery: null` → UI shows N/A).
- Bluetooth on some laptop VMs lacks `AF_BLUETOOTH` — use native OS Python for the bonus client.

## Contributions (template)

- **Member A:** WiFi server, car telemetry, motor command mapping, Bluetooth RFCOMM server.
- **Member B:** Electron UI (HTML/JS), status display, README / report background paragraph, demo recording.

Adjust names to match your group.
