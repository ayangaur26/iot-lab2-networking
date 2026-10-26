# Lab 2 — IoT Networking (WiFi + Electron, Bluetooth later)

Remote-control the Freenove 4WD over **WiFi TCP**, with an **Electron** UI that sends drive commands and displays live car stats. Bluetooth RFCOMM is implemented as a bonus with the **same command/JSON protocol**.

## Layout

```
Code/Lab2/
  pi/           wifi_server.py, wifi_client.py, car_telemetry.py
  electron/     remote-control desktop app
  bluetooth/    RFCOMM bt_server.py (Pi) + bt_client.py (PC)
  report/       NOTES.md (writeup bullets) + DEMO_VIDEO.md
```

## Protocol

- TCP port **65432** (WiFi) or Bluetooth RFCOMM channel **1**
- Client sends one line: `forward` | `backward` | `left` | `right` | `stop` | `status`
- Server replies with one JSON line, e.g.

```json
{"battery":57.0,"temp_c":48.2,"speed":0.0,"distance":0.45,"moving":"forward","turning":"no"}
```

## Step 2 — WiFi echo / car server (on the Pi)

1. Find the Pi IP:

```bash
hostname -I
```

2. Start the server (motors need root / pigpio-style access as with Lab 1):

```bash
cd ~/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Lab2/pi
# venv is at repo root: ../../../.venv
sudo ../../../.venv/bin/python wifi_server.py
# hardware-free test:
python3 wifi_server.py --dry-run
```

3. From another terminal (Pi or laptop on same Wi‑Fi):

```bash
python3 wifi_client.py 127.0.0.1
# or
python3 wifi_client.py <PI_IP>
```

Try `status`, then `forward`, `left`, `stop`.

## Step 3 — Electron remote UI

On the machine that will show the UI (laptop recommended; Pi works if Node is installed).

If Node is missing on the Pi, user-space install via nvm:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
. ~/.nvm/nvm.sh && nvm install 20
```

Then:

```bash
cd Code/Lab2/electron
npm install
npm start
```

Set **Pi IP** in the window (or edit `DEFAULT_HOST` in `index.js`). Use **WASD / arrow keys**; release key → stop. Stats refresh every 500 ms.

`main.js` enables `nodeIntegration` + `contextIsolation: false` so the renderer can use `require('net')` (as in the lab notes).

## Bluetooth bonus (Step 1, deferred path)

1. Pair PC ↔ Pi (`bluetoothctl`).
2. Get Pi BT MAC: `bluetoothctl show` → Controller.
3. On Pi:

```bash
cd Code/Lab2/bluetooth
sudo ../../../.venv/bin/python bt_server.py --addr AA:BB:CC:DD:EE:FF
```

4. On PC (native Python with `AF_BLUETOOTH`):

```bash
python3 bt_client.py AA:BB:CC:DD:EE:FF
```

## Demo checklist

See [report/DEMO_VIDEO.md](report/DEMO_VIDEO.md). Writeup bullets: [report/NOTES.md](report/NOTES.md).

## Reused Freenove code

- `Code/Server/motor.py` — `Ordinary_Car`
- `Code/Server/adc.py` — battery voltage (channel 2)
- Pi CPU temp from `/sys/class/thermal/thermal_zone0/temp`
