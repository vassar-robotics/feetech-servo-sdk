#!/usr/bin/env python3
"""
Utility functions for Feetech servo operations.
"""

import platform
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


# Feetech register addresses
PRESENT_POSITION = 56


def find_port() -> str:
    """Find robot serial port automatically."""
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
    """Read current positions from motors."""
    positions = {}
    
    for motor_id in motor_ids:
        result = packet_handler.read2ByteTxRx(port_handler, motor_id, PRESENT_POSITION)
        
        if len(result) >= 2:
            position = result[0]
            if result[1] == scs.COMM_SUCCESS:
                positions[motor_id] = position
    
    return positions