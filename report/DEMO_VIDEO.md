# Lab 2 Demo Video Checklist (< 10 minutes)

Aligns with the 20‑point video rubric.

## Before recording

- [ ] Pi and laptop on same Wi‑Fi; `ping <PI_IP>` works
- [ ] `wifi_server.py` running on the Pi (not dry-run for the driving clip)
- [ ] Electron `npm start` with correct Pi IP
- [ ] Clear floor space; battery charged

## Script

### 1. WiFi communication code (~5 pts) — ~2 min

- Open `Code/Lab2/pi/wifi_server.py`
- Hover / show: `serve()`, `CarController.handle()`, JSON reply
- Show `wifi_client.py` briefly OR Electron `sendCommand()` in `index.js`
- Mention port **65432** and command list

### 2. Car moving + getting stats code (~5 pts) — ~2 min

- Show motor burst in `_burst_drive` / `Ordinary_Car.set_motor_model`
- Show `car_telemetry.py`: battery, temp, distance
- Show example JSON reply in the terminal

### 3. Car moving from web interface (~5 pts) — ~2 min

- Full-screen Electron UI
- Press W / arrows; film the car moving forward, turn, stop
- Point at green active arrow keys

### 4. Web interface getting stats (~5 pts) — ~2 min

- Zoom on Battery / Temp / Distance (and Moving / Turning)
- Values updating while idle (`status` poll) and after a move
- Optional: terminal on Pi printing `reply: {...}`

### Closing (~30 s)

- Repo link (GitLab/GitHub) for the report
- Note Bluetooth is bonus / same protocol if you demo it

## Tips

- Narrate while hovering the exact functions (`handle`, `sendCommand`, `snapshot`)
- If Wi‑Fi is flaky, record UI + car in one continuous take first, then cut in code walkthrough
