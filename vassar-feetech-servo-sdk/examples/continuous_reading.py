#!/usr/bin/env python3
"""Example of continuous reading with custom callback."""

import time
from datetime import datetime
from vassar_feetech_servo_sdk import ServoReader


class PositionLogger:
    """Example class that logs position data."""
    
    def __init__(self):
        self.start_time = time.time()
        self.reading_count = 0
        
    def log_positions(self, positions):
        """Custom callback to log position data."""
        self.reading_count += 1
        elapsed = time.time() - self.start_time
        
        # Calculate average position
        avg_position = sum(positions.values()) / len(positions) if positions else 0
        
        # Log data
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Reading #{self.reading_count} "
              f"(elapsed: {elapsed:.1f}s)")
        print(f"  Average position: {avg_position:.0f} "
              f"({avg_position/4095*100:.1f}%)")
        print(f"  Motors: {list(positions.keys())}")
        print()


def main():
    # Create reader and logger
    reader = ServoReader()
    logger = PositionLogger()
    
    # Use context manager for automatic cleanup
    with reader:
        print("Starting continuous reading at 10Hz...")
        print("Press Ctrl+C to stop\n")
        
        try:
            # Read continuously with custom callback
            reader.read_positions_continuous(
                motor_ids=[1, 2, 3, 4, 5, 6],
                callback=logger.log_positions,
                frequency=10.0  # 10Hz
            )
        except KeyboardInterrupt:
            print(f"\nTotal readings: {logger.reading_count}")
            print(f"Duration: {time.time() - logger.start_time:.1f}s")


if __name__ == "__main__":
    main()