"""
Vassar Feetech Servo SDK - A Python library for reading positions from Feetech servos.

This package provides both a Python API and command-line interface for 
reading joint positions from robots using Feetech servos (STS/SMS/HLS series).
"""

__version__ = "0.1.0"
__author__ = "Vassar Robotics"
__email__ = "hello@vassarrobotics.com"

from .reader import ServoReader, find_servo_port
from .exceptions import ServoReaderError, PortNotFoundError, ConnectionError

# The scservo_sdk is bundled with this package and can be imported as:
# import scservo_sdk
# or
# from vassar_feetech_servo_sdk import scservo_sdk (after installation)

__all__ = [
    "ServoReader",
    "find_servo_port",
    "ServoReaderError",
    "PortNotFoundError", 
    "ConnectionError",
]