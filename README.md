# IoT Lab 2 — Self-Driving Car Networking (WiFi + Electron)

Remote-control the Freenove 4WD over **WiFi TCP**, with an **Electron** UI that sends drive commands and displays live car stats.

**Later:** Bluetooth remote control (skipped for now).

## Layout

```
pi/           wifi_server.py, wifi_client.py, car_telemetry.py
electron/     remote-control desktop app
dist/         lab2-electron.tar.gz (copy to laptop, then npm install)
```

## Protocol

- TCP port **65432**
- Client sends one line: `forward` | `backward` | `left` | `right` | `stop` | `status`
- Server replies with one JSON line, e.g.

```json
{"battery":57.0,"temp_c":48.2,"speed":0.0,"distance":0.45,"moving":"forward","turning":"no"}
```

## WiFi car server (on the Pi)

1. Find the Pi IP:

```bash
hostname -I
```

2. Start the server:

```bash
cd pi
# from the Freenove kit tree, use the project venv if you have one:
# sudo ../../../.venv/bin/python wifi_server.py
sudo python3 wifi_server.py
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

## Electron remote UI (on your laptop)

```bash
# from this repo, or unpack dist/lab2-electron.tar.gz
cd electron
npm install
npm start
```

If Node is missing:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
. ~/.nvm/nvm.sh && nvm install 20
```

Set **Pi IP** in the window (or edit `DEFAULT_HOST` in `index.js`). Use **WASD / arrow keys**; release key → stop. Stats refresh every 500 ms.

`main.js` enables `nodeIntegration` + `contextIsolation: false` so the renderer can use `require('net')`.

## Reused Freenove code

- `motor.py` — `Ordinary_Car` (add Freenove `Code/Server` to `PYTHONPATH` or run beside that tree)
- `adc.py` — battery voltage (channel 2)
- Pi CPU temp from `/sys/class/thermal/thermal_zone0/temp`
