#!/usr/bin/env python3
"""Minimal teleoperation: auto-detect leader/follower by voltage.

Leader arm: voltage < 9V
Follower arm: voltage > 9V
"""

import time
from vassar_feetech_servo_sdk import ServoController

# Configuration
SERVO_IDS = [1, 2, 3, 4, 5, 6]
SERVO_TYPE = "sts"  # or "hls"
PORT1 = "/dev/ttyUSB0"
PORT2 = "/dev/ttyUSB1"
VOLTAGE_THRESHOLD = 9.0  # Volts
FREQUENCY = 20  # Hz

# Check voltage on first port to determine leader/follower
ctrl1 = ServoController(SERVO_IDS, SERVO_TYPE, PORT1)
ctrl2 = ServoController(SERVO_IDS, SERVO_TYPE, PORT2)

with ctrl1, ctrl2:
    # Read voltage from first servo on port1
    voltage1 = ctrl1.read_voltage(SERVO_IDS[0])
    
    if voltage1 < VOLTAGE_THRESHOLD:
        leader, follower = ctrl1, ctrl2
        print(f"Port1: Leader (voltage: {voltage1:.1f}V)")
    else:
        leader, follower = ctrl2, ctrl1
        print(f"Port1: Follower (voltage: {voltage1:.1f}V)")
    
    print(f"Teleoperation started at {FREQUENCY}Hz. Ctrl+C to stop.")
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
