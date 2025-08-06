#!/usr/bin/env python3
"""
Minimal script to read joint positions from SO101 robot.

Example usage:
python read_leader_positions.py
"""

import argparse
import platform
import time
from typing import Dict, List

try:
    from serial.tools import list_ports
except ImportError:
    print("ERROR: pyserial not installed. Please install with: pip install pyserial")
    exit(1)

try:
    import scservo_sdk as scs
except ImportError:
    print("ERROR: scservo_sdk not found")
    exit(1)


def find_port() -> str:
    """Find robot serial port."""
    ports = []
    
    if platform.system() == "Darwin":  # macOS
        ports = [p.device for p in list_ports.comports() 
                if "usbmodem" in p.device or "usbserial" in p.device]
    elif platform.system() == "Linux":
        ports = [p.device for p in list_ports.comports() 
                if "ttyUSB" in p.device or "ttyACM" in p.device]
    else:  # Windows
        ports = [p.device for p in list_ports.comports() if "COM" in p.device]
    
    if not ports:
        raise RuntimeError("No robot port found")
    
    return ports[0]  # Return first port found


def read_positions(port_handler, packet_handler, motor_ids: List[int]) -> Dict[int, int]:
    """Read positions from motors using group sync read."""
    positions = {}
    
    # Create group sync read instance
    # Address 56 is PRESENT_POSITION, reading 2 bytes
    groupSyncRead = scs.GroupSyncRead(packet_handler, 56, 2)
    
    # Add all motor IDs to the group
    for motor_id in motor_ids:
        if not groupSyncRead.addParam(motor_id):
            print(f"[ID:{motor_id:03d}] groupSyncRead addParam failed")
            continue
    
    # Perform the group read
    comm_result = groupSyncRead.txRxPacket()
    if comm_result != scs.COMM_SUCCESS:
        print(f"GroupSyncRead failed: {packet_handler.getTxRxResult(comm_result)}")
        groupSyncRead.clearParam()
        return positions
    
    # Extract data for each motor
    for motor_id in motor_ids:
        # Check if data is available
        data_result, error = groupSyncRead.isAvailable(motor_id, 56, 2)
        if data_result:
            # Get position value
            position = groupSyncRead.getData(motor_id, 56, 2)
            positions[motor_id] = position
        else:
            print(f"[ID:{motor_id:03d}] groupSyncRead getData failed")
        
        if error != 0:
            print(f"[ID:{motor_id:03d}] {packet_handler.getRxPacketError(error)}")
    
    # Clear parameters for next read
    groupSyncRead.clearParam()
    
    return positions


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
    packet_handler = scs.sms_sts(port_handler)  # Using SMS/STS series handler
    
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