"""Command-line interface for vassar_feetech_servo_sdk."""

import argparse
import sys
from typing import List

from .controller import ServoController, find_servo_port
from .exceptions import ServoReaderError


def parse_motor_ids(motor_ids_str: str) -> List[int]:
    """Parse motor IDs from comma-separated string."""
    try:
        return [int(id.strip()) for id in motor_ids_str.split(",")]
    except ValueError:
        raise ValueError(f"Invalid motor IDs format: {motor_ids_str}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Control Feetech servos (STS/HLS series)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Read from motors 1-6 continuously at 30Hz
  vassar-servo
  
  # Set servos to middle position
  vassar-servo --set-middle
  
  # Read from specific motors at 60Hz
  vassar-servo --motor-ids 1,3,5 --hz 60
  
  # Use specific port and servo type
  vassar-servo --port /dev/ttyUSB0 --servo-type hls
  
  # Just read once and exit
  vassar-servo --once
        """
    )
    
    parser.add_argument(
        "--motor-ids", 
        type=str, 
        default="1,2,3,4,5,6",
        help="Comma-separated motor IDs (default: 1,2,3,4,5,6)"
    )
    
    parser.add_argument(
        "--port", 
        type=str, 
        help="Serial port (auto-detect if not specified)"
    )
    
    parser.add_argument(
        "--baudrate",
        type=int,
        default=1000000,
        help="Communication baudrate (default: 1000000)"
    )
    
    parser.add_argument(
        "--servo-type",
        type=str,
        choices=["sts", "hls"],
        default="sts",
        help="Servo type: 'sts' or 'hls' (default: sts)"
    )
    
    parser.add_argument(
        "--hz", 
        type=float, 
        default=30.0, 
        help="Reading frequency in Hz (default: 30.0)"
    )
    
    parser.add_argument(
        "--once",
        action="store_true",
        help="Read once and exit instead of continuous reading"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (useful for --once)"
    )
    
    parser.add_argument(
        "--set-middle",
        action="store_true",
        help="Set servos to middle position (2048) and exit"
    )
    
    args = parser.parse_args()
    
    try:
        # Parse motor IDs
        motor_ids = parse_motor_ids(args.motor_ids)
        
        # Find port if not specified
        port = args.port
        if not port:
            print("Auto-detecting servo port...")
            port = find_servo_port()
            print(f"Found port: {port}")
        
        # Create controller
        controller = ServoController(
            servo_ids=motor_ids,
            servo_type=args.servo_type,
            port=port,
            baudrate=args.baudrate
        )
        
        print(f"Connecting to {args.servo_type.upper()} servos on {port} at {args.baudrate} baud...")
        controller.connect()
        print("Connected!")
        
        if args.set_middle:
            # Set middle position
            success = controller.set_middle_position()
            sys.exit(0 if success else 1)
        elif args.once:
            # Single read
            positions = controller.read_positions()
            
            if args.json:
                import json
                print(json.dumps(positions))
            else:
                print(f"\n{'Motor':<6} | {'Position':>8} | {'Percent':>7}")
                print("-" * 30)
                for motor_id in sorted(positions.keys()):
                    pos = positions[motor_id]
                    percent = (pos / 4095) * 100
                    print(f"{motor_id:<6} | {pos:>8} | {percent:>6.1f}%")
        else:
            # Continuous read
            print(f"\nReading at {args.hz} Hz. Press Ctrl+C to stop.\n")
            controller.read_positions_continuous(frequency=args.hz)
            
    except ServoReaderError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        if 'controller' in locals():
            controller.disconnect()


if __name__ == "__main__":
    main()