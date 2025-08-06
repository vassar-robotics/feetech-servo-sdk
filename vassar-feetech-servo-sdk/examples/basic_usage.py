#!/usr/bin/env python3
"""Basic example of using vassar_feetech_servo_sdk library."""

from vassar_feetech_servo_sdk import ServoReader

def main():
    # Create reader with auto-detected port
    reader = ServoReader()
    
    try:
        # Connect to servos
        print("Connecting to servos...")
        reader.connect()
        print("Connected!")
        
        # Read single motor
        print("\n--- Reading single motor ---")
        position = reader.read_position(motor_id=1)
        print(f"Motor 1 position: {position} ({position/4095*100:.1f}%)")
        
        # Read multiple motors
        print("\n--- Reading multiple motors ---")
        motor_ids = [1, 2, 3, 4, 5, 6]
        positions = reader.read_positions(motor_ids)
        
        for motor_id in sorted(positions.keys()):
            pos = positions[motor_id]
            percent = pos / 4095 * 100
            print(f"Motor {motor_id}: {pos:4d} ({percent:5.1f}%)")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        reader.disconnect()
        print("\nDisconnected")


if __name__ == "__main__":
    main()