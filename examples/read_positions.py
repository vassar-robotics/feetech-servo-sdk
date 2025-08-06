#!/usr/bin/env python3
"""
Example: Read servo positions continuously.

Example usage:
python read_positions.py
"""

import argparse
import sys
import time
sys.path.append('..')  # Add parent directory to path

try:
    import scservo_sdk as scs
except ImportError:
    print("ERROR: scservo_sdk not found")
    exit(1)

from feetech_utils import find_port, read_positions


def main():
    parser = argparse.ArgumentParser(description="Read robot positions")
    parser.add_argument("--motor_ids", type=str, default="1,2,3,4,5,6",
                       help="Motor IDs (default: 1,2,3,4,5,6)")
    parser.add_argument("--port", type=str, help="Serial port")
    parser.add_argument("--hz", type=int, default=30, help="Frequency (default: 30)")
    
    args = parser.parse_args()
    motor_ids = [int(id.strip()) for id in args.motor_ids.split(",")]
    
    # Find port
    port = args.port if args.port else find_port()
    print(f"Using port: {port}")
    
    # Connect
    port_handler = scs.PortHandler(port)
    packet_handler = scs.PacketHandler(0)
    
    if not port_handler.openPort():
        print(f"Failed to open port {port}")
        return
        
    if not port_handler.setBaudRate(1000000):
        print("Failed to set baudrate")
        return
    
    print(f"Connected! Reading at {args.hz} Hz")
    print("Press Ctrl+C to stop\n")
    
    try:
        loop_time = 1.0 / args.hz
        
        while True:
            start = time.perf_counter()
            
            # Read and display positions
            positions = read_positions(port_handler, packet_handler, motor_ids)
            
            # Clear previous lines
            print("\033[K" * (len(motor_ids) + 3), end="")
            print(f"\033[{len(motor_ids) + 3}A", end="")
            
            # Display
            print(f"{'Motor':<6} | {'Pos':>4} | {'%':>5}")
            print("-" * 20)
            for motor_id in sorted(positions.keys()):
                pos = positions[motor_id]
                percent = (pos / 4095) * 100
                print(f"{motor_id:<6} | {pos:>4} | {percent:>4.0f}%")
            
            # Maintain rate
            elapsed = time.perf_counter() - start
            if elapsed < loop_time:
                time.sleep(loop_time - elapsed)
                
    except KeyboardInterrupt:
        print("\n\nStopped")
    finally:
        port_handler.closePort()


if __name__ == "__main__":
    main() 