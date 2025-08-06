#!/usr/bin/env python3
"""Example of continuous reading with custom callback."""

import time
from datetime import datetime
from vassar_feetech_servo_sdk import ServoController


class PositionLogger:
    """Example class that logs position data."""
    
    def __init__(self):
        self.start_time = time.time()
        self.reading_count = 0
        
    def log_positions(self, positions):
        """Custom callback to log position data."""
        self.reading_count += 1
        elapsed = time.time() - self.start_time
        
        # Log data
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Reading #{self.reading_count} "
              f"(elapsed: {elapsed:.1f}s)")
        
        # Print each servo's position
        for motor_id in sorted(positions.keys()):
            pos = positions[motor_id]
            percent = pos / 4095 * 100
            print(f"  Motor {motor_id}: {pos:4d} ({percent:5.1f}%)")
        print()


def main():
    # Define your servo configuration
    servo_ids = [1, 2, 3, 4, 5, 6]
    servo_type = "sts"  # or "hls" for HLS servos
    
    # Create controller and logger
    controller = ServoController(servo_ids=servo_ids, servo_type=servo_type)
    logger = PositionLogger()
    
    # Use context manager for automatic cleanup
    with controller:
        print(f"Starting continuous reading of {servo_type.upper()} servos at 10Hz...")
        print("Press Ctrl+C to stop\n")
        
        try:
            # Read continuously with custom callback
            controller.read_positions_continuous(
                callback=logger.log_positions,
                frequency=10.0  # 10Hz
            )
        except KeyboardInterrupt:
            print(f"\nTotal readings: {logger.reading_count}")
            print(f"Duration: {time.time() - logger.start_time:.1f}s")


if __name__ == "__main__":
    main()