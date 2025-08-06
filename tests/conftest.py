"""Pytest configuration for vassar_feetech_servo_sdk tests."""

import sys
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))