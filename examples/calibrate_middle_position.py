#!/usr/bin/env python3
"""
Example: Calibrate servos to their middle position (2048).

Uses the special torque=128 command to calibrate current position to 2048.
The calibration takes effect immediately.

Based on the Feetech STS Servos manual:
http://doc.feetech.cn/#/prodinfodownload?srcType=FT-SMS-STS-emanual-229f4476422d4059abfb1cb0

Example usage:
python calibrate_middle_position.py
"""

import argparse
import sys
import time
from typing import List
sys.path.append('..')  # Add parent directory to path

try:
    import scservo_sdk as scs
except ImportError:
    print("ERROR: scservo_sdk not found")
    exit(1)

from feetech_utils import find_port, read_positions


# Feetech register addresses
TORQUE_ENABLE = 40  # Write 128 to calibrate current position to 2048


def set_middle_position(port_handler, packet_handler, motor_ids: List[int]):
    """Set servos to middle position using the torque=128 method.
    
    From STS3215 documentation:
    Address 40 (0x28) - Torque Switch: Write 128 to calibrate current position to 2048
    """
    print("\nSetting middle position...")
    
    # Use the special torque=128 command to calibrate current position to 2048
    for motor_id in motor_ids:
        packet_handler.write1ByteTxRx(port_handler, motor_id, TORQUE_ENABLE, 128)
        time.sleep(0.05)  # Give it time to process
    
    # Verify positions
    time.sleep(0.1)
    positions = read_positions(port_handler, packet_handler, motor_ids)
    
    print("\nVerifying...")
    all_good = True
    for motor_id in sorted(positions.keys()):
        pos = positions[motor_id]
        diff = pos - 2048
        if abs(diff) > 10:
            all_good = False
            print(f"Motor {motor_id}: {pos} (off by {diff:+d})")
    
    if all_good:
        print("✓ Success! All servos set to middle position (2048)")
    else:
        print("⚠ Some servos are not at 2048.")


def main():
    parser = argparse.ArgumentParser(description="Set servos to middle position")
    parser.add_argument("--motor_ids", type=str, default="1,2,3,4,5,6",
                       help="Motor IDs (default: 1,2,3,4,5,6)")
    parser.add_argument("--port", type=str, help="Serial port")
    
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
    
    try:
        set_middle_position(port_handler, packet_handler, motor_ids)
        
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        port_handler.closePort()


if __name__ == "__main__":
    main()