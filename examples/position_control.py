#!/usr/bin/env python3
"""Example of position control with STS/HLS servos."""

from vassar_feetech_servo_sdk import ServoController
import time

def main():
    # Define your servo configuration
    servo_ids = [1, 2, 3]  # Adjust to match your servo IDs
    servo_type = "hls"     # Change to "sts" for STS servos
    
    # Create controller
    controller = ServoController(servo_ids=servo_ids, servo_type=servo_type)
    
    try:
        # Connect to servos
        print(f"Connecting to {servo_type.upper()} servos...")
        controller.connect()
        print("Connected!")
        
        # Read current positions
        print("\n--- Current positions ---")
        positions = controller.read_all_positions()
        for motor_id, pos in sorted(positions.items()):
            print(f"Motor {motor_id}: {pos} ({pos/4095*360:.1f}°)")
        
        # Example 1: Simple position control
        print("\n--- Moving to specific positions ---")
        target_positions = {
            1: 1024,   # ~90° (1024/4095 * 360°)
            2: 2048,   # ~180° (middle position)
            3: 3072    # ~270°
        }
        
        print("Target positions:")
        for motor_id, pos in sorted(target_positions.items()):
            print(f"Motor {motor_id}: {pos} ({pos/4095*360:.1f}°)")
        
        results = controller.write_position(target_positions)
        
        for motor_id, success in sorted(results.items()):
            status = "✓" if success else "✗"
            print(f"Motor {motor_id}: {status}")
        
        # Wait for movement to complete
        print("\nWaiting 2 seconds for movement...")
        time.sleep(2)
        
        # Example 2: Position control with speed and acceleration
        print("\n--- Position control with speed and acceleration ---")
        print("Moving with controlled speed (60 = ~44 RPM) and acceleration...")
        
        target_positions = {
            1: 4095,   # Max position
            2: 0,      # Min position
            3: 2048    # Middle position
        }
        
        # Speed: 60 units = 60 * 0.732 = ~44 RPM
        # Acceleration: 50 units = 50 * 8.7 = 435°/s²
        results = controller.write_position(target_positions, speed=60, acceleration=50)
        
        for motor_id, success in sorted(results.items()):
            status = "✓" if success else "✗"
            print(f"Motor {motor_id}: {status}")
        
        time.sleep(3)
        
        # Example 3: Position control with torque limit (HLS only)
        if servo_type == "hls":
            print("\n--- Position control with torque limit (HLS only) ---")
            print("Moving to positions with 50% torque limit...")
            
            target_positions = {
                1: 1024,   # ~90°
                2: 3072,   # ~270°
                3: 2048    # ~180°
            }
            
            torque_limits = {
                1: 0.5,    # 50% torque limit
                2: 0.8,    # 80% torque limit
                3: 0.3     # 30% torque limit
            }
            
            # Using both torque limit and speed control
            results = controller.write_position(target_positions, torque_limits, speed=40, acceleration=30)
            
            for motor_id, success in sorted(results.items()):
                status = "✓" if success else "✗"
                print(f"Motor {motor_id}: {status}")
            
            time.sleep(3)
        
        # Example 4: Sequential movement
        print("\n--- Sequential movement example ---")
        print("Moving motors one by one...")
        
        positions_sequence = [
            {1: 0, 2: 0, 3: 0},           # All to 0°
            {1: 2048, 2: 0, 3: 0},        # Motor 1 to middle
            {1: 2048, 2: 2048, 3: 0},     # Motor 2 to middle
            {1: 2048, 2: 2048, 3: 2048},  # Motor 3 to middle
            {1: 4095, 2: 4095, 3: 4095}   # All to max position
        ]
        
        for i, positions in enumerate(positions_sequence):
            print(f"\nStep {i+1}:")
            for motor_id, pos in sorted(positions.items()):
                print(f"  Motor {motor_id}: {pos} ({pos/4095*360:.1f}°)")
            
            controller.write_position(positions)
            time.sleep(1)
        
        # Example 5: Return to middle
        print("\n--- Returning to middle position ---")
        middle_positions = {motor_id: 2048 for motor_id in servo_ids}
        controller.write_position(middle_positions)
        print("All motors returned to middle position")
        
    except ValueError as e:
        print(f"\nError: {e}")
        if "torque limit" in str(e).lower():
            print("Note: Torque limit is only supported for HLS servos.")
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
