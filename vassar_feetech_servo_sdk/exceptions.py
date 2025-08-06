"""Custom exceptions for vassar_feetech_servo_sdk package."""


class ServoReaderError(Exception):
    """Base exception for all ServoController errors."""
    pass


class PortNotFoundError(ServoReaderError):
    """Raised when no suitable serial port is found."""
    pass


class ConnectionError(ServoReaderError):
    """Raised when connection to servos fails."""
    pass


class CommunicationError(ServoReaderError):
    """Raised when communication with servos fails."""
    pass