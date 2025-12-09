#!/usr/bin/env python3
"""
Simple test script to send a single binary packet with type 0x47 to avr-core.

Usage:
  # create a venv (optional) and install dependency
  python3 -m venv .venv && source .venv/bin/activate
  pip install websocket-client

  # run (default URL ws://localhost:5001)
  python3 scripts/test_packet_0x47.py --url ws://localhost:5001

What it does:
  - Connects to the WebSocket server
  - Sends a single-byte binary frame containing 0x47
  - Waits briefly for any server responses and prints them

Note: `docker-compose-google.yml` maps container port 5001 to host 5001 by default.
"""

import argparse
import time

try:
    import websocket
except Exception:
    raise SystemExit("Missing dependency: pip install websocket-client")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="ws://localhost:5001", help="WebSocket URL (default: ws://localhost:5001)")
    parser.add_argument("--wait", type=float, default=2.0, help="Seconds to wait for server responses (default 2.0)")
    parser.add_argument("--connect-timeout", type=float, default=10.0, help="Connection/handshake timeout in seconds (default 10)")
    parser.add_argument("--trace", action="store_true", help="Enable websocket-client trace output")
    parser.add_argument("--retries", type=int, default=3, help="Number of connect retries (default 3)")
    args = parser.parse_args()

    if args.trace:
        websocket.enableTrace(True)

    print(f"Connecting to {args.url} (timeout={args.connect_timeout}s, retries={args.retries})")
    ws = None
    attempt = 0
    while attempt < args.retries:
        attempt += 1
        try:
            ws = websocket.create_connection(args.url, timeout=args.connect_timeout)
            break
        except Exception as e:
            print(f"Connect attempt {attempt} failed:", repr(e))
            if attempt < args.retries:
                backoff = 1 * attempt
                print(f"Retrying in {backoff}s...")
                time.sleep(backoff)
            else:
                print("All connection attempts failed")
                return 2

    try:
        # set short recv timeout while waiting for messages
        ws.settimeout(1.0)
        payload = bytes([0x47])
        print(f"Sending payload: {payload!r}")
        # send as binary frame
        ws.send(payload, opcode=websocket.ABNF.OPCODE_BINARY)
        print("Sent. Waiting for server responses...")
        # wait some seconds and try to read messages
        end = time.time() + args.wait
        while time.time() < end:
            try:
                msg = ws.recv()
                print("Received from server:", repr(msg))
            except websocket._exceptions.WebSocketTimeoutException:
                # nothing received in the short recv timeout; continue waiting
                continue
            except Exception as e:
                print("Receive error (non-fatal):", repr(e))
                break
        print("Done — closing connection")
    finally:
        try:
            ws.close()
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main() or 0)
