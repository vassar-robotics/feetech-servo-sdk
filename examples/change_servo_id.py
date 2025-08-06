#!/usr/bin/env python3
"""Example of changing a servo's ID."""

from vassar_feetech_servo_sdk import ServoController, find_servo_port

def main():
    # Current servo configuration
    current_id = 1  # The current ID of the servo you want to change
    new_id = 2     # The new ID you want to assign
    
    # Create controller with just the current ID
    # Note: After changing the ID, you'll need to update this
    controller = ServoController(servo_ids=[current_id], servo_type="sts")
    
    try:
        # Connect to servo
        print(f"Connecting to servo with ID {current_id}...")
        controller.connect()
        print("Connected!")
        
        # Read current position to verify communication
        print(f"\nVerifying servo ID {current_id} is responding...")
        position = controller.read_position(current_id)
        print(f"✓ Servo ID {current_id} position: {position}")
        
        # Change the servo ID
        print(f"\n--- Changing servo ID from {current_id} to {new_id} ---")
        success = controller.set_motor_id(
            current_id=current_id,
            new_id=new_id,
            confirm=True  # Will ask for user confirmation
        )
        
        if success:
            print("\n🎉 ID change successful!")
            print("\nNext steps:")
            print("1. Power cycle your servo (turn power off and on)")
            print("2. Update your code to use the new ID")
            print(f"   Example: ServoController(servo_ids=[{new_id}], servo_type='sts')")
        else:
            print("\nID change was cancelled or failed.")
            
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        controller.disconnect()
        print("\nDisconnected")


def verify_new_id():
    """
    Helper function to verify the servo responds with its new ID.
    Run this after power cycling the servo.
    """
    new_id = 2  # The new ID you assigned
    
    controller = ServoController(servo_ids=[new_id], servo_type="sts")
    
    try:
        print(f"\nVerifying servo with new ID {new_id}...")
        controller.connect()
        
        position = controller.read_position(new_id)
        print(f"✓ Success! Servo ID {new_id} position: {position}")
        
    except Exception as e:
        print(f"❌ Failed to communicate with ID {new_id}: {e}")
    finally:
        controller.disconnect()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        # Run: python change_servo_id.py verify
        # To verify the servo responds with its new ID
        verify_new_id()
    else:
        # Run: python change_servo_id.py
        # To change the servo ID
        main()