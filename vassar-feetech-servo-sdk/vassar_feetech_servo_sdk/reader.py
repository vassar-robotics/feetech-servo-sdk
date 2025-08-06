"""Core functionality for reading Feetech servo positions."""

import platform
import time
from typing import Dict, List, Optional, Union

try:
    from serial.tools import list_ports
except ImportError:
    raise ImportError("pyserial not installed. Please install with: pip install pyserial")

import scservo_sdk as scs

from .exceptions import PortNotFoundError, ConnectionError, CommunicationError


def find_servo_port() -> str:
    """
    Find robot serial port automatically.
    
    Returns:
        str: The first suitable serial port found.
        
    Raises:
        PortNotFoundError: If no suitable port is found.
    """
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
        raise PortNotFoundError("No suitable serial port found for servo communication")
    
    return ports[0]  # Return first port found


class ServoReader:
    """
    A class for reading positions from Feetech servos.
    
    This class provides methods to connect to and read positions from
    Feetech servos (STS/SMS/HLS series) via serial communication.
    
    Attributes:
        port (str): Serial port path
        baudrate (int): Communication baudrate
        servo_type (str): Type of servo ('sms_sts', 'hls', or 'scscl')
    """
    
    PRESENT_POSITION_ADDR = 56  # Address for present position register
    POSITION_DATA_LENGTH = 2    # Bytes to read for position
    
    def __init__(self, port: Optional[str] = None, baudrate: int = 1000000, 
                 servo_type: str = "sms_sts"):
        """
        Initialize ServoReader.
        
        Args:
            port: Serial port path. If None, will attempt auto-detection.
            baudrate: Communication baudrate (default: 1000000).
            servo_type: Type of servo - 'sms_sts', 'hls', or 'scscl' (default: 'sms_sts').
        """
        self.port = port if port else find_servo_port()
        self.baudrate = baudrate
        self.servo_type = servo_type.lower()
        
        self.port_handler = None
        self.packet_handler = None
        self._connected = False
        
    def connect(self) -> None:
        """
        Connect to the servos.
        
        Raises:
            ConnectionError: If connection fails.
        """
        if self._connected:
            return
            
        # Initialize port handler
        self.port_handler = scs.PortHandler(self.port)
        
        # Initialize packet handler based on servo type
        if self.servo_type == "sms_sts":
            self.packet_handler = scs.sms_sts(self.port_handler)
        elif self.servo_type == "hls":
            self.packet_handler = scs.hls(self.port_handler)
        elif self.servo_type == "scscl":
            self.packet_handler = scs.scscl(self.port_handler)
        else:
            raise ValueError(f"Unknown servo type: {self.servo_type}")
        
        # Open port
        if not self.port_handler.openPort():
            raise ConnectionError(f"Failed to open port {self.port}")
            
        # Set baudrate
        if not self.port_handler.setBaudRate(self.baudrate):
            self.port_handler.closePort()
            raise ConnectionError(f"Failed to set baudrate to {self.baudrate}")
            
        self._connected = True
        
    def disconnect(self) -> None:
        """Disconnect from the servos."""
        if self._connected and self.port_handler:
            self.port_handler.closePort()
            self._connected = False
            
    def read_position(self, motor_id: int) -> int:
        """
        Read position from a single motor.
        
        Args:
            motor_id: The ID of the motor to read from.
            
        Returns:
            int: Position value (0-4095).
            
        Raises:
            CommunicationError: If reading fails.
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        position, comm_result, error = self.packet_handler.ReadPos(motor_id)
        
        if comm_result != scs.COMM_SUCCESS:
            raise CommunicationError(
                f"Failed to read position from motor {motor_id}: "
                f"{self.packet_handler.getTxRxResult(comm_result)}"
            )
            
        if error != 0:
            raise CommunicationError(
                f"Motor {motor_id} error: {self.packet_handler.getRxPacketError(error)}"
            )
            
        return position
        
    def read_positions(self, motor_ids: List[int]) -> Dict[int, int]:
        """
        Read positions from multiple motors using group sync read.
        
        Args:
            motor_ids: List of motor IDs to read from.
            
        Returns:
            dict: Dictionary mapping motor IDs to position values.
            
        Raises:
            CommunicationError: If reading fails.
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        positions = {}
        
        # Create group sync read instance
        groupSyncRead = scs.GroupSyncRead(
            self.packet_handler, 
            self.PRESENT_POSITION_ADDR, 
            self.POSITION_DATA_LENGTH
        )
        
        # Add all motor IDs to the group
        for motor_id in motor_ids:
            if not groupSyncRead.addParam(motor_id):
                print(f"Warning: Failed to add motor {motor_id} to group read")
                continue
        
        # Perform the group read
        comm_result = groupSyncRead.txRxPacket()
        if comm_result != scs.COMM_SUCCESS:
            groupSyncRead.clearParam()
            raise CommunicationError(
                f"Group sync read failed: {self.packet_handler.getTxRxResult(comm_result)}"
            )
        
        # Extract data for each motor
        for motor_id in motor_ids:
            # Check if data is available
            data_result, error = groupSyncRead.isAvailable(
                motor_id, 
                self.PRESENT_POSITION_ADDR, 
                self.POSITION_DATA_LENGTH
            )
            
            if data_result:
                # Get position value
                position = groupSyncRead.getData(
                    motor_id, 
                    self.PRESENT_POSITION_ADDR, 
                    self.POSITION_DATA_LENGTH
                )
                positions[motor_id] = position
            else:
                print(f"Warning: Failed to get data for motor {motor_id}")
            
            if error != 0:
                print(f"Warning: Motor {motor_id} error: "
                      f"{self.packet_handler.getRxPacketError(error)}")
        
        # Clear parameters for next read
        groupSyncRead.clearParam()
        
        return positions
    
    def read_positions_continuous(self, motor_ids: List[int], 
                                  callback=None, frequency: float = 30.0):
        """
        Continuously read positions from motors.
        
        Args:
            motor_ids: List of motor IDs to read from.
            callback: Optional callback function that receives positions dict.
            frequency: Reading frequency in Hz (default: 30.0).
            
        The method will run until KeyboardInterrupt is received.
        """
        if not self._connected:
            self.connect()
            
        loop_time = 1.0 / frequency
        
        try:
            while True:
                start = time.perf_counter()
                
                # Read positions
                positions = self.read_positions(motor_ids)
                
                # Call callback if provided
                if callback:
                    callback(positions)
                else:
                    # Default display
                    self._display_positions(positions)
                
                # Maintain rate
                elapsed = time.perf_counter() - start
                if elapsed < loop_time:
                    time.sleep(loop_time - elapsed)
                    
        except KeyboardInterrupt:
            print("\nStopped")
            
    def _display_positions(self, positions: Dict[int, int]) -> None:
        """Default display function for positions."""
        # Clear previous lines
        print("\033[K" * (len(positions) + 3), end="")
        print(f"\033[{len(positions) + 3}A", end="")
        
        # Display
        print(f"{'Motor':<6} | {'Pos':>4} | {'%':>5}")
        print("-" * 20)
        for motor_id in sorted(positions.keys()):
            pos = positions[motor_id]
            percent = (pos / 4095) * 100
            print(f"{motor_id:<6} | {pos:>4} | {percent:>4.0f}%")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()