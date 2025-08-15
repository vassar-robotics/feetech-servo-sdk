"""
Vassar Feetech Servo SDK - A comprehensive Python SDK for controlling Feetech servos.

This package provides a Python API for controlling Feetech servos (STS/HLS series). 
Features include reading positions, setting middle position, and changing motor IDs.
"""

__version__ = "1.2.0"
__author__ = "Vassar Robotics"
__email__ = "hello@vassarrobotics.com"

from .controller import ServoController, find_servo_port
from .exceptions import ServoReaderError, PortNotFoundError, ConnectionError

# The scservo_sdk is bundled with this package and can be imported as:
# import scservo_sdk
# or
# from vassar_feetech_servo_sdk import scservo_sdk (after installation)

__all__ = [
    "ServoController",
    "find_servo_port",
    "ServoReaderError",
    "PortNotFoundError", 
    "ConnectionError",
]