#!/usr/bin/env python3
"""Example showing different servo types and error handling."""

from vassar_feetech_servo_sdk import (
    ServoController, 
    find_servo_port,
    PortNotFoundError,
    ConnectionError,
    CommunicationError
)


def test_servo_type(servo_type, motor_ids):
    """Test reading from a specific servo type."""
    print(f"\n{'='*50}")
    print(f"Testing {servo_type.upper()} servos")
    print(f"{'='*50}")
    
    try:
        # Find port
        port = find_servo_port()
        print(f"Using port: {port}")
        
        # Create controller for specific servo type
        controller = ServoController(
            servo_ids=motor_ids,
            servo_type=servo_type,
            port=port,
            baudrate=1000000
        )
        
        # Connect
        controller.connect()
        print(f"Connected to {servo_type.upper()} servos")
        
        # Read positions
        positions = controller.read_all_positions()
        
        if positions:
            print(f"\nPositions for {servo_type.upper()} servos:")
            for motor_id, pos in sorted(positions.items()):
                print(f"  Motor {motor_id}: {pos:4d} ({pos/4095*100:5.1f}%)")
        else:
            print("No positions read - check motor IDs")
            
        # Disconnect
        controller.disconnect()
        print(f"\nDisconnected from {servo_type.upper()} servos")
        
    except PortNotFoundError:
        print("ERROR: No servo port found")
        print("Please check:")
        print("  1. Servo controller is connected")
        print("  2. USB drivers are installed")
        
    except ConnectionError as e:
        print(f"ERROR: Failed to connect - {e}")
        print("Please check:")
        print("  1. Correct servo type selected")
        print("  2. Baudrate matches servo configuration")
        print("  3. Power supply is connected")
        
    except CommunicationError as e:
        print(f"ERROR: Communication failed - {e}")
        print("Please check:")
        print("  1. Motor IDs are correct")
        print("  2. Wiring is correct (TX/RX)")
        print("  3. Servos are powered on")
        
    except Exception as e:
        print(f"ERROR: Unexpected error - {e}")


def main():
    """Main function demonstrating different servo types."""
    print("Feetech Servo Type Example")
    print("This example shows how to work with STS and HLS servo types")
    
    # Test motor IDs
    motor_ids = [1, 2, 3, 4, 5, 6]
    
    # Test STS servos (most common)
    test_servo_type("sts", motor_ids)
    
    # Uncomment to test HLS servos:
    # test_servo_type("hls", motor_ids)      # HLS servos with torque control
    
    print("\n" + "="*50)
    print("Example completed")


if __name__ == "__main__":
    main()