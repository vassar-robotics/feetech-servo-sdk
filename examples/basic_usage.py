#!/usr/bin/env python3
"""Basic example of using vassar_feetech_servo_sdk library."""

from vassar_feetech_servo_sdk import ServoController

def main():
    # Define your servo configuration
    servo_ids = [1, 2, 3, 4, 5, 6]
    servo_type = "sts"  # or "hls" for HLS servos
    
    # Create controller
    controller = ServoController(servo_ids=servo_ids, servo_type=servo_type)
    
    try:
        # Connect to servos
        print(f"Connecting to {servo_type.upper()} servos...")
        controller.connect()
        print("Connected!")
        
        # Read all configured servos
        print("\n--- Reading all servo positions ---")
        positions = controller.read_all_positions()
        
        for motor_id in sorted(positions.keys()):
            pos = positions[motor_id]
            percent = pos / 4095 * 100
            print(f"Motor {motor_id}: {pos:4d} ({percent:5.1f}%)")
        
        # Set middle position (optional)
        print("\n--- Setting middle position ---")
        print("Do you want to set all servos to middle position? (y/n)")
        if input().lower() == 'y':
            success = controller.set_middle_position()
            if success:
                print("All servos calibrated to middle position!")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.disconnect()
        print("\nDisconnected")


if __name__ == "__main__":
    main()