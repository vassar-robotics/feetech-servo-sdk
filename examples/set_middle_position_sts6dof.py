#!/usr/bin/env python3
"""Example of setting servos to middle position (2048)."""

from vassar_feetech_servo_sdk import ServoController
from serial.tools import list_ports
import platform


def main():
    # Define your servo configuration
    servo_ids = [1, 2, 3, 4, 5, 6, 7]
    servo_type = "sts" # sts"  # or "hls" for HLS servos
    
    try:
        # Auto-detect the servo port
        port = find_servo_port()
        print(f"Found servo port: {port}")
        
        # Create controller with auto-detected port
        controller = ServoController(servo_ids=servo_ids, servo_type=servo_type, port=port)
        
        # Connect to servos
        print(f"Connecting to {servo_type.upper()} servos...")
        controller.connect()
        
    except Exception as e:
        print(f"Error: {e}")
        return
    
    try:

        
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

def find_servo_port():
    """Find all USB serial ports on the system."""
    print(f"Operating System: {platform.system()}")
    print("\nScanning for USB serial devices...")
    
    ports = list_ports.comports()
    usb_ports = []
    
    for port in ports:
        # Filter for likely USB devices
        if platform.system() == "Windows":
            if "COM" in port.device:
                usb_ports.append(port)
    
    if usb_ports:
        print(f"\nFound {len(usb_ports)} USB serial device(s):")
        for i, port in enumerate(usb_ports):
            print(f"  {i+1}. {port.device} - {port.description}")
            if hasattr(port, 'manufacturer') and port.manufacturer:
                print(f"      Manufacturer: {port.manufacturer}")
            if hasattr(port, 'serial_number') and port.serial_number:
                print(f"      Serial: {port.serial_number}")
        
        # Return the first port (assuming only 1 device as you mentioned)
        return usb_ports[0].device
    else:
        print("\nNo USB serial devices found!")
        return None


if __name__ == "__main__":
    main()