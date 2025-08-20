#!/usr/bin/env python3
"""Minimal teleoperation: auto-detect leader/follower by voltage.

Leader arm: voltage < 9V
Follower arm: voltage > 9V
"""

import platform
import time
from typing import List
from serial.tools import list_ports
from vassar_feetech_servo_sdk import ServoController


def find_servo_ports() -> List[str]:
    """Find available servo ports based on operating system."""
    ports = []
    
    system = platform.system()
    if system == "Darwin":  # macOS
        ports = [p.device for p in list_ports.comports() 
                if "usbmodem" in p.device or "usbserial" in p.device]
    elif system == "Linux":
        ports = [p.device for p in list_ports.comports() 
                if "ttyUSB" in p.device or "ttyACM" in p.device]
    else:  # Windows
        ports = [p.device for p in list_ports.comports() if "COM" in p.device]
    
    return sorted(ports)


def main():
    # Configuration
    SERVO_IDS = [1, 2, 3, 4, 5, 6]
    SERVO_TYPE = "sts"  # or "hls"
    VOLTAGE_THRESHOLD = 9.0  # Volts
    FREQUENCY = 20  # Hz
    
    # Auto-detect ports
    ports = find_servo_ports()
    if len(ports) < 2:
        print(f"Error: Need 2 servo ports but found {len(ports)}")
        if ports:
            print(f"Available ports: {', '.join(ports)}")
        return
    
    print(f"Found ports: {ports[0]}, {ports[1]}")
    
    # Create controllers
    ctrl1 = ServoController(SERVO_IDS, SERVO_TYPE, ports[0])
    ctrl2 = ServoController(SERVO_IDS, SERVO_TYPE, ports[1])
    
    with ctrl1, ctrl2:
        # Read voltage from first servo on first port
        voltage1 = ctrl1.read_voltage(SERVO_IDS[0])
        
        # Leader arm should have voltage ~5V, follower arm ~12V
        if voltage1 < VOLTAGE_THRESHOLD:
            leader, follower = ctrl1, ctrl2
            print(f"{ports[0]}: Leader (voltage: {voltage1:.1f}V)")
            print(f"{ports[1]}: Follower")
        else:
            leader, follower = ctrl2, ctrl1
            print(f"{ports[0]}: Follower (voltage: {voltage1:.1f}V)")
            print(f"{ports[1]}: Leader")
        
        print(f"\nTeleoperation started at {FREQUENCY}Hz. Ctrl+C to stop.")
        loop_time = 1.0 / FREQUENCY
        
        try:
            while True:
                start = time.perf_counter()
                
                # Read leader positions and write to follower
                positions = leader.read_positions()
                follower.write_position(positions)
                
                # Maintain rate
                elapsed = time.perf_counter() - start
                if elapsed < loop_time:
                    time.sleep(loop_time - elapsed)
                    
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
