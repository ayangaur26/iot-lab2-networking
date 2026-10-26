#!/usr/bin/env python3
"""
Lab 2 WiFi server (Steps 2–3).

Listens on TCP 0.0.0.0:65432. Each client connection sends one command line;
the server drives the car (unless --dry-run) and replies with one JSON status line.

Commands:
  forward | backward | left | right | stop | status
  (also accepts legacy Electron keycodes 87/83/65/68 for WASD)

Usage (from Code/Lab2/pi, with Freenove Server on PYTHONPATH):
  cd ~/Freenove_4WD_Smart_Car_Kit_for_Raspberry_Pi/Code/Lab2/pi
  sudo ../../../.venv/bin/python wifi_server.py
  python3 wifi_server.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
import threading
import time
from typing import Optional

# Freenove motor/ADC live in Code/Server
_SERVER_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Server")
)
if _SERVER_DIR not in sys.path:
    sys.path.insert(0, _SERVER_DIR)

from car_telemetry import CarTelemetry  # noqa: E402

HOST = "0.0.0.0"
PORT = 65432

# Timed bursts so a single TCP request moves the car briefly then stops.
BURST_S = 0.45
DRIVE_PWM = 1600
TURN_PWM = 1800
# Rough crawl speed used only for distance bookkeeping (cm/s → m)
DRIVE_CM_PER_SEC = 22.0

# Map UI / keycodes → canonical command
_ALIASES = {
    "87": "forward",  # W
    "83": "backward",  # S
    "65": "left",  # A
    "68": "right",  # D
    "w": "forward",
    "s": "backward",
    "a": "left",
    "d": "right",
    "up": "forward",
    "down": "backward",
}


class CarController:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.telemetry = CarTelemetry(dry_run=dry_run)
        self._motor = None
        self._lock = threading.Lock()
        if not dry_run:
            try:
                from motor import Ordinary_Car  # type: ignore

                self._motor = Ordinary_Car()
                self._motor.set_motor_model(0, 0, 0, 0)
                print("[car] Ordinary_Car ready")
            except Exception as e:
                print(f"[car] motor init failed ({e}); forcing dry-run")
                self.dry_run = True
                self.telemetry.dry_run = True

    def close(self) -> None:
        with self._lock:
            if self._motor is not None:
                try:
                    self._motor.set_motor_model(0, 0, 0, 0)
                    self._motor.close()
                except Exception:
                    pass
                self._motor = None
        self.telemetry.close()

    def _apply_pwm(self, fl: int, bl: int, fr: int, br: int) -> None:
        if self._motor is None:
            print(f"[dry-run] PWM fl={fl} bl={bl} fr={fr} br={br}")
            return
        self._motor.set_motor_model(fl, bl, fr, br)

    def handle(self, raw: str) -> str:
        cmd = raw.strip().lower()
        cmd = _ALIASES.get(cmd, cmd)
        if not cmd:
            cmd = "status"

        with self._lock:
            if cmd == "status":
                pass
            elif cmd == "stop":
                self._apply_pwm(0, 0, 0, 0)
                self.telemetry.note_motion("stopped", "no")
            elif cmd == "forward":
                self._burst_drive(DRIVE_PWM, DRIVE_PWM, DRIVE_PWM, DRIVE_PWM, "forward", "no")
            elif cmd == "backward":
                self._burst_drive(-DRIVE_PWM, -DRIVE_PWM, -DRIVE_PWM, -DRIVE_PWM, "backward", "no")
            elif cmd == "left":
                # spin left
                self._burst_drive(-TURN_PWM, -TURN_PWM, TURN_PWM, TURN_PWM, "stopped", "left")
            elif cmd == "right":
                self._burst_drive(TURN_PWM, TURN_PWM, -TURN_PWM, -TURN_PWM, "stopped", "right")
            else:
                # Unknown: treat as echo-friendly status (lab Step 2 tutorial)
                print(f"[server] unknown cmd {raw!r} — returning status")

            return self.telemetry.to_json_line()

    def _burst_drive(
        self,
        fl: int,
        bl: int,
        fr: int,
        br: int,
        moving: str,
        turning: str,
    ) -> None:
        self._apply_pwm(fl, bl, fr, br)
        t0 = time.monotonic()
        time.sleep(BURST_S)
        self._apply_pwm(0, 0, 0, 0)
        dt = time.monotonic() - t0
        dist = 0.0
        if moving in ("forward", "backward"):
            dist = (DRIVE_CM_PER_SEC * dt) / 100.0
        # Record what we just did for the status pane (motors already stopped).
        label_moving = moving if turning == "no" else "stopped"
        self.telemetry.note_motion(label_moving, turning, dist, dt)
        self.telemetry.speed_mps = 0.0


def serve(dry_run: bool = False) -> None:
    car = CarController(dry_run=dry_run)
    print(f"[wifi] listening on {HOST}:{PORT}  dry_run={dry_run}")
    print("[wifi] commands: forward|backward|left|right|stop|status")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(5)
        s.settimeout(1.0)
        try:
            while True:
                try:
                    client, client_info = s.accept()
                except socket.timeout:
                    continue
                with client:
                    print("server recv from:", client_info)
                    try:
                        data = client.recv(1024)
                    except ConnectionResetError:
                        continue
                    if not data:
                        continue
                    text = data.decode("utf-8", errors="replace").strip()
                    # Strip CR if Electron sends \r\n
                    text = text.replace("\r", "")
                    print("  cmd:", text)
                    reply = car.handle(text)
                    client.sendall(reply.encode("utf-8"))
                    print("  reply:", reply.strip())
        except KeyboardInterrupt:
            print("\nClosing socket")
        finally:
            car.close()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Lab 2 WiFi car server")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="No motor/ADC hardware — log PWM and return fake-friendly JSON",
    )
    p.add_argument("--host", default=HOST, help="Bind address (default 0.0.0.0)")
    p.add_argument("--port", type=int, default=PORT)
    return p.parse_args()


def main() -> None:
    global HOST, PORT
    args = parse_args()
    HOST = args.host
    PORT = args.port
    serve(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
