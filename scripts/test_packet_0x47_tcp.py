#!/usr/bin/env python3
"""Send a single raw TCP packet byte 0x47 to the AVR core TCP server.

Usage: python3 scripts/test_packet_0x47_tcp.py --host 127.0.0.1 --port 5001

The server in the container listens on a raw TCP socket (not WebSocket).
This script connects, sends one byte (0x47) and prints basic status.
"""
import argparse
import socket
import sys
import time


def send_byte(host: str, port: int, timeout: float) -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        # send single byte 0x47
        s.sendall(b"\x47")
        # optionally try to read a short response (non-blocking with timeout)
        try:
            data = s.recv(1024)
            if data:
                print("Received reply:", data)
        except socket.timeout:
            pass
        s.close()
        return 0
    except Exception as e:
        print("Connection failed:", e)
        try:
            s.close()
        except Exception:
            pass
        return 2


def main():
    parser = argparse.ArgumentParser(description="Send raw packet 0x47 to AVR core TCP server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5001)
    parser.add_argument("--timeout", type=float, default=5.0, help="connect timeout seconds")
    parser.add_argument("--retries", type=int, default=3, help="number of attempts")
    parser.add_argument("--delay", type=float, default=1.0, help="delay between retries seconds")
    args = parser.parse_args()

    for attempt in range(1, args.retries + 1):
        print(f"Attempt {attempt}/{args.retries}: connect to {args.host}:{args.port} (timeout={args.timeout}s)")
        rc = send_byte(args.host, args.port, args.timeout)
        if rc == 0:
            print("Sent 0x47 successfully")
            sys.exit(0)
        if attempt < args.retries:
            time.sleep(args.delay)

    print("All attempts failed")
    sys.exit(2)


if __name__ == '__main__':
    main()
