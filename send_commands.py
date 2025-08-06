#!/usr/bin/env python3
"""
Script to read joint positions from SO101 robot and send them over UDP.

Example usage:
python send_commands.py --target-ip 192.168.1.100 --target-port 5000
"""

import argparse
import platform
import socket
import struct
import time
from typing import Dict, List

try:
    from serial.tools import list_ports
except ImportError:
    print("ERROR: pyserial not installed. "
          "Please install with: pip install pyserial")
    exit(1)

try:
    import scservo_sdk as scs
except ImportError:
    print("ERROR: scservo_sdk not found")
    exit(1)


def find_port() -> str:
    """Find robot serial port."""
    ports = []

    if platform.system() == "Darwin":  # macOS
        ports = [p.device for p in list_ports.comports()
                 if "usbmodem" in p.device or "usbserial" in p.device]
    elif platform.system() == "Linux":
        ports = [p.device for p in list_ports.comports()
                 if "ttyUSB" in p.device or "ttyACM" in p.device]
    else:  # Windows
        ports = [p.device for p in list_ports.comports() if "COM" in p.device]
    
    if not ports:
        raise RuntimeError("No robot port found")
    
    return ports[0]  # Return first port found


def read_positions(port_handler, packet_handler,
                   motor_ids: List[int]) -> Dict[int, int]:
    """Read positions from motors."""
    positions = {}
    
    for motor_id in motor_ids:
        # PRESENT_POSITION = 56
        result = packet_handler.read2ByteTxRx(port_handler, motor_id, 56)
        
        if len(result) >= 2:
            position = result[0]
            if result[1] == scs.COMM_SUCCESS:
                positions[motor_id] = position
    
    return positions


def create_udp_socket(target_ip: str, target_port: int) -> socket.socket:
    """Create UDP socket for sending position data."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # Set socket options for low latency
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_TOS, 0x10)  # IPTOS_LOWDELAY
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024)  # Small buffer
    return sock


def send_positions_udp(sock: socket.socket, target_ip: str, target_port: int,
                       positions: Dict[int, int], timestamp: float):
    """Send position data over UDP with minimal latency."""
    # Create compact binary message for lowest latency
    # Format: timestamp (8 bytes) + num_motors (1 byte) +
    # motor_data (3 bytes per motor: id + position)

    num_motors = len(positions)
    message = struct.pack('<dB', timestamp, num_motors)
    
    for motor_id, position in sorted(positions.items()):
        # Pack motor ID (1 byte) and position (2 bytes)
        message += struct.pack('<BH', motor_id, position)
    
    sock.sendto(message, (target_ip, target_port))


def main():
    parser = argparse.ArgumentParser(
        description="Read robot positions and send over UDP")
    parser.add_argument("--motor_ids", type=str, default="1,2,3,4,5,6",
                        help="Motor IDs (default: 1,2,3,4,5,6)")
    parser.add_argument("--port", type=str, help="Serial port")
    parser.add_argument("--hz", type=int, default=30,
                        help="Frequency (default: 30)")
    parser.add_argument("--target-ip", type=str, required=True,
                        help="Target IP address to send positions to")
    parser.add_argument("--target-port", type=int, default=5000,
                        help="Target UDP port (default: 5000)")
    
    args = parser.parse_args()
    motor_ids = [int(id.strip()) for id in args.motor_ids.split(",")]
    
    # Find port
    port = args.port if args.port else find_port()
    print(f"Using port: {port}")
    
    # Create UDP socket
    udp_sock = create_udp_socket(args.target_ip, args.target_port)
    print(f"Sending UDP to {args.target_ip}:{args.target_port}")
    
    # Connect to robot
    port_handler = scs.PortHandler(port)
    packet_handler = scs.PacketHandler(0)
    
    if not port_handler.openPort():
        print(f"Failed to open port {port}")
        return
        
    if not port_handler.setBaudRate(1000000):
        print("Failed to set baudrate")
        return

    print(f"Connected! Reading at {args.hz} Hz")
    print("Press Ctrl+C to stop\n")
    
    try:
        loop_time = 1.0 / args.hz
        sent_count = 0
        
        while True:
            start = time.perf_counter()
            timestamp = time.time()
            
            # Read positions
            positions = read_positions(port_handler, packet_handler, motor_ids)
            
            # Send over UDP
            if positions:
                send_positions_udp(udp_sock, args.target_ip, args.target_port,
                                   positions, timestamp)
                sent_count += 1
            
            # Clear previous lines
            print("\033[K" * (len(motor_ids) + 4), end="")
            print(f"\033[{len(motor_ids) + 4}A", end="")
            
            # Display
            print(f"{'Motor':<6} | {'Pos':>4} | {'%':>5}")
            print("-" * 20)
            for motor_id in sorted(positions.keys()):
                pos = positions[motor_id]
                percent = (pos / 4095) * 100
                print(f"{motor_id:<6} | {pos:>4} | {percent:>4.0f}%")
            print(f"\nSent: {sent_count} messages")
            
            # Maintain rate
            elapsed = time.perf_counter() - start
            if elapsed < loop_time:
                time.sleep(loop_time - elapsed)
                
    except KeyboardInterrupt:
        print("\n\nStopped")
    finally:
        port_handler.closePort()
        udp_sock.close()


if __name__ == "__main__":
    main()