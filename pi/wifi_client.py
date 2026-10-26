#!/usr/bin/env python3
"""
Lab 2 WiFi test client (Step 2).

Talks to wifi_server.py on the Pi. Send commands like:
  forward | backward | left | right | stop | status
Or any other text (echoed / handled by the server).

Usage:
  python3 wifi_client.py [HOST]
  python3 wifi_client.py 192.168.10.188
"""

from __future__ import annotations

import socket
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
PORT = 65432


def main() -> None:
    print(f"Connecting to {HOST}:{PORT} …")
    print("Commands: forward, backward, left, right, stop, status  (or quit)")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5.0)
        s.connect((HOST, PORT))
        while True:
            text = input("Enter your message: ").strip()
            if not text:
                continue
            if text.lower() == "quit":
                break
            s.sendall((text + "\n").encode("utf-8"))
            data = s.recv(4096)
            print("from server:", data.decode("utf-8", errors="replace").strip())


if __name__ == "__main__":
    main()
