#!/usr/bin/env python3
"""Example of torque control with HLS servos."""

from vassar_feetech_servo_sdk import ServoController
import time

def main():
    # Define your HLS servo configuration
    servo_ids = [1, 2, 3]  # Adjust to match your servo IDs
    
    # Create controller for HLS servos
    controller = ServoController(servo_ids=servo_ids, servo_type="hls")
    
    try:
        # Connect to servos
        print("Connecting to HLS servos...")
        controller.connect()
        print("Connected!")
        
        # Read current positions
        print("\n--- Current positions ---")
        positions = controller.read_all_positions()
        for motor_id, pos in sorted(positions.items()):
            print(f"Motor {motor_id}: {pos}")
        
        # Example 1: Simple torque control
        print("\n--- Applying torque ---")
        print("Motor 1: 0.4 (40% forward)")
        print("Motor 2: -0.3 (30% reverse)")
        print("Motor 3: 0 (no torque)")
        
        torque_values = {
            1: 0.4,   # Positive = one direction (40% of max torque)
            2: -0.3,  # Negative = opposite direction (30% of max torque)
            3: 0       # Zero = no torque
        }
        
        results = controller.write_torque(torque_values)
        
        for motor_id, success in sorted(results.items()):
            status = "✓" if success else "✗"
            print(f"Motor {motor_id}: {status}")
        
        # Let motors run with torque for a bit
        print("\nApplying torque for 15 seconds...")
        time.sleep(15)
        
        # Example 2: Stop all motors
        print("\n--- Stopping all motors ---")
        stop_torques = {motor_id: 0.0 for motor_id in servo_ids}
        results = controller.write_torque(stop_torques)
        print("All motors stopped")
        
        time.sleep(1)
        
        # Example 3: Variable torque
        print("\n--- Variable torque example ---")
        print("Gradually increasing torque on motor 1...")
        
        for i in range(0, 11):  # 0 to 10 steps
            torque = i * 0.1  # 0.00 to 1.00 in steps of 0.10
            controller.write_torque({1: torque})
            print(f"Torque: {torque:.2f} ({int(torque * 100)}% forward)")
            time.sleep(0.5)
        
        # Stop motor 1
        controller.write_torque({1: 0.0})
        
        # Example 4: Setting operating modes manually
        print("\n--- Manual mode control ---")
        print("Setting motor 1 to position mode...")
        if controller.set_operating_mode(1, 0):
            print("✓ Motor 1 set to position mode")
        
        print("Setting motor 2 to speed mode...")
        if controller.set_operating_mode(2, 1):
            print("✓ Motor 2 set to speed mode")
            
        print("Setting motor 3 back to torque mode...")
        if controller.set_operating_mode(3, 2):
            print("✓ Motor 3 set to torque mode")
            
    except ValueError as e:
        print(f"\nError: {e}")
        print("Make sure you're using HLS servos. STS servos don't support torque control.")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # disconnect() will automatically disable all servos
        if 'controller' in locals():
            controller.disconnect()
            print("Disconnected")


if __name__ == "__main__":
    main()