#!/usr/bin/env python3
"""Example of reading voltage from servos."""

from vassar_feetech_servo_sdk import ServoController

# Configure servos
SERVO_IDS = [1, 2, 3, 4, 5, 6]
SERVO_TYPE = "sts"  # or "hls"

with ServoController(SERVO_IDS, SERVO_TYPE) as controller:
    # Read voltage from single servo
    voltage = controller.read_voltage(SERVO_IDS[0])
    print(f"Servo {SERVO_IDS[0]} voltage: {voltage:.1f}V")
    
    # Read voltages from all servos
    print("\nAll servo voltages:")
    voltages = controller.read_voltages()
    for motor_id, v in sorted(voltages.items()):
        print(f"  Servo {motor_id}: {v:.1f}V")
