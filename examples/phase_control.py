#!/usr/bin/env python3
"""Example of reading and setting servo phase values."""

from vassar_feetech_servo_sdk import ServoController


def main():
    # Configure servos
    servo_ids = [1, 2, 3]
    servo_type = "sts"  # or "hls"
    
    # Create controller - phase will be automatically set to 0 during connect()
    controller = ServoController(servo_ids, servo_type)
    
    with controller:
        print("\n--- Reading current phase values ---")
        for motor_id in servo_ids:
            try:
                phase = controller.read_phase(motor_id)
                print(f"Motor {motor_id}: Phase = {phase}")
                
                # Decode phase bits (for reference)
                print(f"  BIT0 (Drive phase): {'reverse' if phase & 1 else 'normal'}")
                print(f"  BIT3 (Speed feedback): {'reverse' if phase & 8 else 'normal'}")
                print(f"  BIT7 (Position feedback): {'reverse' if phase & 128 else 'normal'}")
            except Exception as e:
                print(f"Motor {motor_id}: Error reading phase - {e}")
        
        # Example: Manually set different phase values
        print("\n--- Setting custom phase values ---")
        print("WARNING: Phase register is a special function byte.")
        print("Only modify if you understand the servo behavior!")
        
        # Example: Set motor 1 to phase 0 (all normal)
        if controller.set_phase(1, 0):
            print(f"Motor 1: Phase set to 0 (all normal)")
        
        # Example: Set motor 2 to phase 128 (position feedback reverse)
        if controller.set_phase(2, 128):
            print(f"Motor 2: Phase set to 128 (position feedback reverse)")
        
        # The servos will be automatically set back to phase 0 
        # the next time ServoController connects to them


if __name__ == "__main__":
    main()
