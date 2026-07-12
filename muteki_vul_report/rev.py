#!/usr/bin/env python3


from __future__ import annotations

import argparse
import selectors
import socket
import sys


def run_listener(host: str, port: int) -> None:
    sel = selectors.DefaultSelector()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen(1)
        print(f"[+] listening on {host}:{port}", flush=True)

        conn, addr = server.accept()
        with conn:
            print(f"[+] connection from {addr[0]}:{addr[1]}", flush=True)
            conn.setblocking(False)
            sys.stdin.flush()
            sel.register(conn, selectors.EVENT_READ, "socket")
            sel.register(sys.stdin, selectors.EVENT_READ, "stdin")

            while True:
                for key, _ in sel.select():
                    if key.data == "socket":
                        data = conn.recv(4096)
                        if not data:
                            print("\n[-] connection closed", flush=True)
                            return
                        sys.stdout.buffer.write(data)
                        sys.stdout.buffer.flush()
                    elif key.data == "stdin":
                        line = sys.stdin.buffer.readline()
                        if not line:
                            return
                        conn.sendall(line)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Local reverse shell listener for authorized Muteki validation."
    )
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="listen host, default: 0.0.0.0",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=4444,
        help="listen port, default: 4444",
    )
    args = parser.parse_args()
    run_listener(args.host, args.port)


if __name__ == "__main__":
    main()
