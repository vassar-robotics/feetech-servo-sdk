#!/usr/bin/env python3
"""Example of setting servos to middle position (2048)."""

from vassar_feetech_servo_sdk import ServoController

def main():
    # Define your servo configuration
    servo_ids = [1, 2, 3, 4, 5, 6, 7]
    servo_type = "hls"  # or "hls" for HLS servos
    
    # Create controller
    controller = ServoController(servo_ids=servo_ids, servo_type=servo_type, port="/dev/tty.usbmodem5A7A0581001")
    
    try:
        # Connect to servos
        print(f"Connecting to {servo_type.upper()} servos...")
        controller.connect()
        print("Connected!")
        
        # Read current positions before calibration
        print("\n--- Current positions before calibration ---")
        positions_before = controller.read_all_positions()
        
        for motor_id in sorted(positions_before.keys()):
            pos = positions_before[motor_id]
            diff = pos - 2048
            print(f"Motor {motor_id}: {pos:4d} (off by {diff:+4d} from middle)")
        
        # Set middle position
        print("\n--- Setting all servos to middle position (2048) ---")
        print("This will calibrate the current physical position as 2048.")
        input("Press Enter to continue (or Ctrl+C to cancel)...")
        
        success = controller.set_middle_position()
        
        if success:
            print("\n✓ All servos successfully calibrated to middle position!")
            
            # Read positions after calibration
            print("\n--- Positions after calibration ---")
            positions_after = controller.read_all_positions()
            
            for motor_id in sorted(positions_after.keys()):
                pos = positions_after[motor_id]
                print(f"Motor {motor_id}: {pos:4d}")
        else:
            print("\n⚠ Some servos failed to calibrate properly")
            
    except KeyboardInterrupt:
        print("\nCalibration cancelled")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        controller.disconnect()
        print("\nDisconnected")


if __name__ == "__main__":
    main()