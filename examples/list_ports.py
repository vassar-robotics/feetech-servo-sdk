#!/usr/bin/env python3
"""Example of listing available servo ports."""

from vassar_feetech_servo_sdk import find_servo_port


def main():
    try:
        # Get first available port
        first_port = find_servo_port()
        print(f"First available port: {first_port}")
        
        # Get all available ports
        all_ports = find_servo_port(return_all=True)
        print(f"\nAll available ports ({len(all_ports)} found):")
        for i, port in enumerate(all_ports):
            print(f"  {i+1}. {port}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
