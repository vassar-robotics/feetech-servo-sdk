"""
Minimal script to read joint positions from SO101 robot.

Example usage:
python read_leader_positions.py
"""

import argparse
import json
import platform
import time
import zmq
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


def main():
    parser = argparse.ArgumentParser(description="Read robot positions")
    parser.add_argument("--motor_ids", type=str, default="1,2,3,4,5,6",
                        help="Motor IDs (default: 1,2,3,4,5,6)")
    parser.add_argument("--port", type=str, help="Serial port")
    parser.add_argument("--hz", type=int, default=10,
                        help="Frequency (default: 10)")

    args = parser.parse_args()
    motor_ids = [int(id.strip()) for id in args.motor_ids.split(",")]

    # Find port
    port = args.port if args.port else find_port()
    print(f"Using port: {port}")

    # Connect
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

    # connect on zmq
    c = zmq.Context().socket(zmq.PUSH)
    c.connect("tcp://10.1.10.85:5000")

    try:
        loop_time = 1.0 / args.hz

        while True:
            start = time.perf_counter()

            # Read and display positions
            positions = read_positions(port_handler, packet_handler, motor_ids)

            # Prepare JSON with joint labels
            joint_dict = {f"joint{motor_id}": pos
                          for motor_id, pos in positions.items()}
            c.send_string(json.dumps(joint_dict))

            # Clear previous lines
            print("\033[K" * (len(motor_ids) + 3), end="")
            print(f"\033[{len(motor_ids) + 3}A", end="")

            # Display
            print(f"{'Motor':<6} | {'Pos':>4} | {'%':>5}")
            print("-" * 20)
            for motor_id in sorted(positions.keys()):
                pos = positions[motor_id]
                percent = (pos / 4095) * 100
                print(f"{motor_id:<6} | {pos:>4} | {percent:>4.0f}%")

            # Maintain rate
            elapsed = time.perf_counter() - start
            if elapsed < loop_time:
                time.sleep(loop_time - elapsed)

    except KeyboardInterrupt:
        print("\n\nStopped")
    finally:
        port_handler.closePort()


if __name__ == "__main__":
    main()