#!/usr/bin/env python3
"""
Lab 2 Step 2 Section 1 — minimal WiFi echo server (tutorial baseline).

For the full car server see wifi_server.py.
"""

from __future__ import annotations

import socket

HOST = "0.0.0.0"
PORT = 65432


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Echo server on {HOST}:{PORT}")
        try:
            while True:
                client, client_info = s.accept()
                print("server recv from:", client_info)
                with client:
                    data = client.recv(1024)
                    if data:
                        print(data)
                        client.sendall(data)
        except KeyboardInterrupt:
            print("Closing socket")


if __name__ == "__main__":
    main()
