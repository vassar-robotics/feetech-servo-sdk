#!/usr/bin/env python3
"""
Minimal UDP receiver for robot joint positions.

Usage:
python receive_positions.py --port 5000
"""

import argparse
import socket
import struct
import time


def main():
    parser = argparse.ArgumentParser(description="Receive robot positions over UDP")
    parser.add_argument("--port", type=int, default=5000, help="UDP port to listen on")
    parser.add_argument("--bind-ip", type=str, default="0.0.0.0", help="IP to bind to")
    args = parser.parse_args()

    # Create UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.bind_ip, args.port))
    
    print(f"Listening on {args.bind_ip}:{args.port}")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            # Receive data
            data, addr = sock.recvfrom(1024)
            
            # Unpack header: timestamp (8 bytes) + num_motors (1 byte)
            timestamp, num_motors = struct.unpack('<dB', data[:9])
            
            # Unpack motor data
            positions = {}
            offset = 9
            for _ in range(num_motors):
                motor_id, position = struct.unpack('<BH', data[offset:offset+3])
                positions[motor_id] = position
                offset += 3
            
            # Display
            print(f"\rFrom {addr[0]} - Motors: {dict(sorted(positions.items()))}", end="", flush=True)
            
    except KeyboardInterrupt:
        print("\n\nStopped")
    finally:
        sock.close()


if __name__ == "__main__":
    main()