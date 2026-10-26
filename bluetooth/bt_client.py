#!/usr/bin/env python3
"""
Lab 2 Bluetooth RFCOMM client (run on the PC / laptop).

Requires Python 3.9+ with AF_BLUETOOTH (native Windows/Linux; not all VMs).

Usage:
  python3 bt_client.py AA:BB:CC:DD:EE:FF
"""

from __future__ import annotations

import socket
import sys

CHANNEL = 1


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 bt_client.py <PI_BT_MAC>")
        raise SystemExit(2)
    if not hasattr(socket, "AF_BLUETOOTH"):
        raise SystemExit("AF_BLUETOOTH not available in this Python")

    addr = sys.argv[1]
    print(f"Connecting RFCOMM to {addr} ch {CHANNEL} …")
    sock = socket.socket(
        socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM
    )
    sock.connect((addr, CHANNEL))
    print("Connected. Commands: forward|backward|left|right|stop|status|quit")
    try:
        while True:
            text = input("cmd> ").strip()
            if not text:
                continue
            if text.lower() == "quit":
                break
            sock.sendall((text + "\n").encode("utf-8"))
            data = sock.recv(4096)
            print("from pi:", data.decode("utf-8", errors="replace").strip())
    finally:
        sock.close()


if __name__ == "__main__":
    main()
