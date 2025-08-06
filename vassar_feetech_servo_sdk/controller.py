"""Core functionality for controlling Feetech servos (STS/HLS series)."""

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


class ServoController:
    """
    A comprehensive controller for Feetech servos (STS/HLS series).
    
    This class provides methods to:
    - Read positions from servos
    - Set middle position (calibrate to 2048)
    - Write position targets (coming soon)
    - Write torque targets (coming soon)
    
    Attributes:
        port (str): Serial port path
        servo_ids (List[int]): List of servo IDs to control
        servo_type (str): Type of servo ('sts' or 'hls')
        baudrate (int): Communication baudrate
    """
    
    PRESENT_POSITION_ADDR = 56  # Address for present position register
    POSITION_DATA_LENGTH = 2    # Bytes to read for position
    
    def __init__(self, servo_ids: List[int], servo_type: str = "sts", 
                 port: Optional[str] = None, baudrate: int = 1000000):
        """
        Initialize ServoController.
        
        Args:
            servo_ids: List of servo IDs to control (e.g., [1, 2, 3, 4, 5, 6]).
            servo_type: Type of servo - 'sts' or 'hls' (default: 'sts').
            port: Serial port path. If None, will attempt auto-detection.
            baudrate: Communication baudrate (default: 1000000).
        """
        self.servo_ids = servo_ids
        self.servo_type = servo_type.lower()
        self.port = port if port else find_servo_port()
        self.baudrate = baudrate
        
        self.port_handler = None
        self.packet_handler = None
        self._connected = False
        
        # Validate servo type
        if self.servo_type not in ['sts', 'hls']:
            raise ValueError(f"Unsupported servo type: {self.servo_type}. Use 'sts' or 'hls'")
        
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
        if self.servo_type == "sts":
            self.packet_handler = scs.sms_sts(self.port_handler)  # STS uses the sms_sts protocol
        elif self.servo_type == "hls":
            self.packet_handler = scs.hls(self.port_handler)
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
        
    def read_positions(self, motor_ids: Optional[List[int]] = None) -> Dict[int, int]:
        """
                Read positions from multiple motors using group sync read.
        
        Args:
            motor_ids: List of motor IDs to read from. If None, uses self.servo_ids.
        
        Returns:
            dict: Dictionary mapping motor IDs to position values.
        
        Raises:
            CommunicationError: If reading fails.
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        if motor_ids is None:
            motor_ids = self.servo_ids
            
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
    
    def set_middle_position(self, motor_ids: Optional[List[int]] = None) -> bool:
        """
        Set servos to middle position (2048).
        
        For STS servos: Uses the special torque=128 command.
        For HLS servos: Uses the reOfsCal offset calibration method.
        
        Args:
            motor_ids: List of motor IDs to calibrate. If None, uses self.servo_ids.
            
        Returns:
            bool: True if all servos successfully set to middle position.
            
        Raises:
            ConnectionError: If not connected.
            CommunicationError: If calibration fails.
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        if motor_ids is None:
            motor_ids = self.servo_ids
            
        if self.servo_type == "hls":
            # HLS servos use reOfsCal method
            print("\nSetting middle position using HLS offset calibration...")
            all_success = True
            
            for motor_id in motor_ids:
                # Calibrate current position to 2048
                comm_result, error = self.packet_handler.reOfsCal(motor_id, 2048)
                if comm_result != scs.COMM_SUCCESS:
                    print(f"Motor {motor_id}: {self.packet_handler.getTxRxResult(comm_result)}")
                    all_success = False
                elif error != 0:
                    print(f"Motor {motor_id}: {self.packet_handler.getRxPacketError(error)}")
                    all_success = False
                else:
                    print(f"Motor {motor_id}: Calibrated to 2048 ✓")
                    
            if not all_success:
                raise CommunicationError("Failed to calibrate some HLS servos")
                
        else:
            # STS servos use torque=128 method
            print("\nSetting middle position using sync write...")
            
            # Feetech register address for torque enable
            TORQUE_ENABLE = 40  # Write 128 to calibrate current position to 2048
            
            # Create a GroupSyncWrite instance
            group_sync_write = scs.GroupSyncWrite(self.packet_handler, TORQUE_ENABLE, 1)
            
            # Add all motors to the sync write
            for motor_id in motor_ids:
                success = group_sync_write.addParam(motor_id, [128])
                if not success:
                    raise CommunicationError(f"Failed to add motor {motor_id} to sync write")
            
            # Send the sync write command
            comm_result = group_sync_write.txPacket()
            if comm_result != scs.COMM_SUCCESS:
                raise CommunicationError(
                    f"Sync write failed: {self.packet_handler.getTxRxResult(comm_result)}"
                )
            
            # Clear the sync write parameters
            group_sync_write.clearParam()
        
        # Give servos time to process the calibration
        time.sleep(0.2)
        
        # Verify positions
        positions = self.read_positions(motor_ids)
        
        print("\nVerifying middle position...")
        all_good = True
        for motor_id in sorted(positions.keys()):
            pos = positions[motor_id]
            diff = pos - 2048
            if abs(diff) > 10:
                all_good = False
                print(f"Motor {motor_id}: {pos} (off by {diff:+d})")
            else:
                print(f"Motor {motor_id}: {pos} ✓")
        
        if all_good:
            print("✓ Success! All servos set to middle position (2048)")
        else:
            print("⚠ Some servos are not at 2048")
            
        return all_good
    
    def read_all_positions(self) -> Dict[int, int]:
        """
        Read positions from all configured servos.
        
        Returns:
            dict: Dictionary mapping motor IDs to position values.
        """
        return self.read_positions(self.servo_ids)
    
    def read_positions_continuous(self, motor_ids: Optional[List[int]] = None, 
                                  callback=None, frequency: float = 30.0):
        """
        Continuously read positions from motors.
        
        Args:
            motor_ids: List of motor IDs to read from. If None, uses self.servo_ids.
            callback: Optional callback function that receives positions dict.
                     If not provided, positions are read but not displayed.
            frequency: Reading frequency in Hz (default: 30.0).
            
        The method will run until KeyboardInterrupt is received.
        """
        if not self._connected:
            self.connect()
            
        if motor_ids is None:
            motor_ids = self.servo_ids
            
        loop_time = 1.0 / frequency
        
        try:
            while True:
                start = time.perf_counter()
                
                # Read positions
                positions = self.read_positions(motor_ids)
                
                # Call callback if provided
                if callback:
                    callback(positions)
                
                # Maintain rate
                elapsed = time.perf_counter() - start
                if elapsed < loop_time:
                    time.sleep(loop_time - elapsed)
                    
        except KeyboardInterrupt:
            print("\nStopped")

    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()