#!/usr/bin/env python3
"""
Lab 2 Bluetooth RFCOMM server (Step 1 bonus — PC sockets path).

Same command / JSON protocol as wifi_server.py:
  forward | backward | left | right | stop | status

Setup (once on the Pi):
  - Pair laptop with the Pi (bluetoothctl)
  - Optional bluez -C / sdptool SP as in the lab writeup
  - Put this Pi's BT MAC in --addr (bluetoothctl show → Controller)

Usage:
  cd Code/Lab2/bluetooth
  sudo ../../../.venv/bin/python bt_server.py --addr AA:BB:CC:DD:EE:FF
  python3 bt_server.py --addr AA:BB:CC:DD:EE:FF --dry-run
"""

from __future__ import annotations

import argparse
import os
import socket
import sys
import time

_PI_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pi"))
_SERVER_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "Server")
)
for p in (_PI_DIR, _SERVER_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

# Reuse WiFi car controller
from wifi_server import CarController  # noqa: E402

CHANNEL = 1


def serve(addr: str, dry_run: bool = False) -> None:
    if not hasattr(socket, "AF_BLUETOOTH"):
        raise SystemExit("AF_BLUETOOTH missing — need system Python with BlueZ support")

    car = CarController(dry_run=dry_run)
    print(f"[bt] RFCOMM server on {addr} channel {CHANNEL} dry_run={dry_run}")

    server = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
    )
    try:
        server.bind((addr, CHANNEL))
        server.listen(1)
        print("[bt] waiting for PC client …")
        while True:
            client, info = server.accept()
            print("[bt] connected:", info)
            with client:
                buf = ""
                while True:
                    try:
                        chunk = client.recv(1024)
                    except ConnectionResetError:
                        break
                    if not chunk:
                        break
                    buf += chunk.decode("utf-8", errors="replace")
                    while "\n" in buf or "\r" in buf:
                        # split on newline
                        for sep in ("\r\n", "\n", "\r"):
                            if sep in buf:
                                line, buf = buf.split(sep, 1)
                                break
                        else:
                            break
                        line = line.strip()
                        if not line:
                            continue
                        print("[bt] cmd:", line)
                        reply = car.handle(line)
                        client.sendall(reply.encode("utf-8"))
                        print("[bt] reply:", reply.strip())
            print("[bt] client disconnected — waiting again")
    except KeyboardInterrupt:
        print("\n[bt] shutting down")
    finally:
        try:
            server.close()
        except Exception:
            pass
        car.close()


def main() -> None:
    p = argparse.ArgumentParser(description="Lab 2 Bluetooth RFCOMM car server")
    p.add_argument(
        "--addr",
        required=True,
        help="This Pi's Bluetooth MAC (bluetoothctl show)",
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()
    serve(args.addr, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
