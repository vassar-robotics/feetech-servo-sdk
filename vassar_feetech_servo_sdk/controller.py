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
            # Always disable servos before disconnecting
            self.disable_all_servos()
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
    


    
    def set_motor_id(self, current_id: int, new_id: int, confirm: bool = True) -> bool:
        """
        Set a new ID for a connected servo.
        
        WARNING: This permanently changes the servo's ID in EEPROM. The servo will need
        to be power cycled or rebooted for the change to take effect.
        
        Args:
            current_id: The current ID of the servo to change.
            new_id: The new ID to assign (0-253).
            confirm: Whether to ask for user confirmation (default: True).
            
        Returns:
            bool: True if ID was successfully changed.
            
        Raises:
            ConnectionError: If not connected.
            ValueError: If IDs are invalid.
            CommunicationError: If communication fails.
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        # Validate IDs
        if not (0 <= current_id <= 253):
            raise ValueError(f"Current ID {current_id} out of range (0-253)")
        if not (0 <= new_id <= 253):
            raise ValueError(f"New ID {new_id} out of range (0-253)")
        if current_id == new_id:
            raise ValueError("Current ID and new ID are the same")
            
        # Memory addresses
        ID_ADDR = 5      # ID register address (same for both STS and HLS)
        LOCK_ADDR = 55   # Lock flag address
        
        # User confirmation
        if confirm:
            print(f"\n⚠️  WARNING: This will permanently change servo ID from {current_id} to {new_id}")
            print("The servo will need to be power cycled for the change to take effect.")
            response = input("Continue? (yes/no): ").strip().lower()
            if response != 'yes':
                print("ID change cancelled.")
                return False
        
        try:
            # Step 1: Verify we can communicate with the servo at current ID
            print(f"\nVerifying communication with servo ID {current_id}...")
            model_number, comm_result, error = self.packet_handler.ping(current_id)
            if comm_result != scs.COMM_SUCCESS:
                raise CommunicationError(
                    f"Cannot communicate with servo ID {current_id}. "
                    f"Error: {self.packet_handler.getTxRxResult(comm_result)}"
                )
            print(f"✓ Servo ID {current_id} found")
            
            # Step 2: Unlock EEPROM
            print("Unlocking EEPROM...")
            if self.servo_type == "sts":
                comm_result, error = self.packet_handler.unLockEprom(current_id)
            elif self.servo_type == "hls":
                comm_result, error = self.packet_handler.unLockEprom(current_id)
            
            if comm_result != scs.COMM_SUCCESS:
                raise CommunicationError(
                    f"Failed to unlock EEPROM: {self.packet_handler.getTxRxResult(comm_result)}"
                )
            print("✓ EEPROM unlocked")
            
            # Step 3: Write new ID
            print(f"Writing new ID {new_id}...")
            comm_result, error = self.packet_handler.write1ByteTxRx(current_id, ID_ADDR, new_id)
            
            if comm_result != scs.COMM_SUCCESS:
                # Try to re-lock EEPROM even if write failed
                self._lock_eeprom_safe(current_id)
                raise CommunicationError(
                    f"Failed to write new ID: {self.packet_handler.getTxRxResult(comm_result)}"
                )
            print(f"✓ New ID {new_id} written")
            
            # Step 4: Lock EEPROM
            print("Locking EEPROM...")
            if self.servo_type == "sts":
                comm_result, error = self.packet_handler.LockEprom(current_id)
            elif self.servo_type == "hls":
                comm_result, error = self.packet_handler.LockEprom(current_id)
                
            if comm_result != scs.COMM_SUCCESS:
                print(f"⚠️  Warning: Failed to lock EEPROM: {self.packet_handler.getTxRxResult(comm_result)}")
            else:
                print("✓ EEPROM locked")
            
            # Give servo time to process
            time.sleep(0.1)
            
            print(f"\n✅ Successfully changed servo ID from {current_id} to {new_id}")
            print("\n⚠️  IMPORTANT: You must now:")
            print(f"   1. Power cycle the servo (turn power off and on)")
            print(f"   2. Update your servo_ids list to include ID {new_id}")
            print(f"   3. Reconnect to use the servo with its new ID")
            
            return True
            
        except Exception as e:
            # Try to ensure EEPROM is locked on any error
            self._lock_eeprom_safe(current_id)
            raise
    
    def _lock_eeprom_safe(self, servo_id: int):
        """Safely attempt to lock EEPROM, ignoring errors."""
        try:
            if self.servo_type == "sts":
                self.packet_handler.LockEprom(servo_id)
            elif self.servo_type == "hls":
                self.packet_handler.LockEprom(servo_id)
        except:
            pass  # Ignore errors when trying to lock
    
    def set_operating_mode(self, motor_id: int, mode: int) -> bool:
        """
        Set the operating mode of a servo.
        
        Args:
            motor_id: The ID of the servo to configure.
            mode: Operating mode (0-3):
                  - 0: Position servo mode
                  - 1: Constant speed mode  
                  - 2: Constant current/torque mode (HLS) or PWM mode (STS)
                  - 3: PWM/Step mode (STS) or PWM open-loop (HLS)
                  
        Returns:
            bool: True if mode was successfully set.
            
        Raises:
            ConnectionError: If not connected.
            ValueError: If mode is invalid.
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        if not (0 <= mode <= 3):
            raise ValueError(f"Invalid mode {mode}. Must be 0-3.")
            
        # Memory addresses
        MODE_ADDR = 33    # Operating mode register (same for both STS and HLS)
        LOCK_ADDR = 55    # Lock flag address
        
        try:
            # Unlock EEPROM
            if self.servo_type == "sts":
                comm_result, error = self.packet_handler.unLockEprom(motor_id)
            else:  # hls
                comm_result, error = self.packet_handler.unLockEprom(motor_id)
                
            if comm_result != scs.COMM_SUCCESS:
                print(f"Warning: Failed to unlock EEPROM for motor {motor_id}")
                return False
                
            # Write new mode
            comm_result, error = self.packet_handler.write1ByteTxRx(motor_id, MODE_ADDR, mode)
            
            if comm_result != scs.COMM_SUCCESS:
                self._lock_eeprom_safe(motor_id)
                print(f"Failed to set mode for motor {motor_id}: {self.packet_handler.getTxRxResult(comm_result)}")
                return False
                
            # Lock EEPROM
            if self.servo_type == "sts":
                comm_result, error = self.packet_handler.LockEprom(motor_id)
            else:  # hls
                comm_result, error = self.packet_handler.LockEprom(motor_id)
                
            if comm_result != scs.COMM_SUCCESS:
                print(f"Warning: Failed to lock EEPROM for motor {motor_id}")
                
            # Give servo time to process
            time.sleep(0.05)
            
            return True
            
        except Exception as e:
            self._lock_eeprom_safe(motor_id)
            print(f"Error setting mode for motor {motor_id}: {e}")
            return False
    
    def write_torque(self, torque_dict: Dict[int, float]) -> Dict[int, bool]:
        """
        Write torque values to HLS servos.
        
        Automatically switches servos to torque mode (mode 2) if needed.
        
        Args:
            torque_dict: Dictionary mapping motor IDs to torque values.
                        Torque range: -1.0 to 1.0 (normalized).
                        -1.0 = full torque reverse direction
                         0.0 = no torque
                         1.0 = full torque forward direction
                        Example: {1: 0.5, 2: -0.3, 3: 0}
                        
        Returns:
            dict: Dictionary mapping motor IDs to success status.
                  Example: {1: True, 2: True, 3: False}
                  
        Raises:
            ConnectionError: If not connected.
            ValueError: If used with STS servos (HLS only).
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        if self.servo_type != "hls":
            raise ValueError("write_torque is only supported for HLS servos. STS servos do not have torque control.")
            
        # Memory addresses
        MODE_ADDR = 33            # Operating mode register
        TORQUE_ENABLE_ADDR = 40   # Torque enable register  
        GOAL_TORQUE_ADDR = 44     # Goal torque register (2 bytes)
        
        results = {}
        
        for motor_id, torque_normalized in torque_dict.items():
            try:
                # Validate normalized torque range
                if not (-1.0 <= torque_normalized <= 1.0):
                    print(f"Warning: Torque {torque_normalized} out of range for motor {motor_id}. Clamping to [-1.0, 1.0]")
                    torque_normalized = max(-1.0, min(1.0, torque_normalized))
                
                # Map torque with direction bit in bit 15
                # Bits 0-10: magnitude (0-2047), Bit 15: direction (0=forward, 1=reverse)
                abs_torque = int(abs(torque_normalized) * 2047 * 0.95)  # 0.95 is for safety factor
                if torque_normalized < 0:
                    torque_value = abs_torque | 0x8000  # Set bit 15 for reverse
                else:
                    torque_value = abs_torque  # Bit 15 = 0 for forward
                
                # Read current mode
                mode_data, comm_result, error = self.packet_handler.read1ByteTxRx(motor_id, MODE_ADDR)
                
                if comm_result != scs.COMM_SUCCESS:
                    print(f"Failed to read mode for motor {motor_id}")
                    results[motor_id] = False
                    continue
                    
                # Switch to torque mode if needed
                if mode_data != 2:
                    print(f"Motor {motor_id} is in mode {mode_data}, switching to torque mode (2)...")
                    if not self.set_operating_mode(motor_id, 2):
                        print(f"Failed to switch motor {motor_id} to torque mode")
                        results[motor_id] = False
                        continue
                        
                # Ensure torque is enabled
                torque_enabled, comm_result, error = self.packet_handler.read1ByteTxRx(motor_id, TORQUE_ENABLE_ADDR)
                if comm_result == scs.COMM_SUCCESS and torque_enabled != 1:
                    comm_result, error = self.packet_handler.write1ByteTxRx(motor_id, TORQUE_ENABLE_ADDR, 1)
                    if comm_result != scs.COMM_SUCCESS:
                        print(f"Warning: Failed to enable torque for motor {motor_id}")
                
                # Write torque value (16-bit signed, little-endian)
                comm_result, error = self.packet_handler.write2ByteTxRx(motor_id, GOAL_TORQUE_ADDR, torque_value)
                
                if comm_result != scs.COMM_SUCCESS:
                    print(f"Failed to write torque for motor {motor_id}: {self.packet_handler.getTxRxResult(comm_result)}")
                    results[motor_id] = False
                else:
                    results[motor_id] = True
                    
            except Exception as e:
                print(f"Error writing torque for motor {motor_id}: {e}")
                results[motor_id] = False
                
        return results
    
    def write_position(self, position_dict: Dict[int, int], 
                      torque_limit_dict: Optional[Dict[int, float]] = None,
                      speed: int = 100,
                      acceleration: int = 0) -> Dict[int, bool]:
        """
        Write position values to servos using efficient SyncWritePosEx method.
        
        Automatically switches servos to position mode (mode 0) if needed.
        
        Args:
            position_dict: Dictionary mapping motor IDs to position values.
                          Position range: 0 to 4095 (0.087°/unit).
                          Example: {1: 2048, 2: 1024, 3: 3072}
                          
            torque_limit_dict: Optional dictionary mapping motor IDs to torque limits.
                              Torque limit range: 0.0 to 1.0 (normalized).
                              Only supported for HLS servos.
                              Example: {1: 0.5, 2: 0.8}
                              
            speed: Goal speed for all servos (0-100, 0.732RPM/unit). 
                   0 = no movement; 100 = max speed. Default: 100 (~73.2 RPM).
                   
            acceleration: Acceleration for all servos (0-254, 8.7°/s²/unit).
                         0 = maximum acceleration (default).
                        
        Returns:
            dict: Dictionary mapping motor IDs to success status.
                  Example: {1: True, 2: True, 3: False}
                  
        Raises:
            ConnectionError: If not connected.
            ValueError: If torque_limit_dict is provided for STS servos.
        """
        if not self._connected:
            raise ConnectionError("Not connected. Call connect() first.")
            
        # Check torque limit compatibility
        if torque_limit_dict and self.servo_type == "sts":
            raise ValueError("Torque limit is only supported for HLS servos. STS servos do not have dynamic torque limit control.")
            
        # Memory addresses
        MODE_ADDR = 33            # Operating mode register (same for STS/HLS)
        TORQUE_ENABLE_ADDR = 40   # Torque enable register
        
        results = {}
        
        # First pass: ensure all servos are in position mode and torque enabled
        for motor_id in position_dict.keys():
            try:
                # Read current mode
                mode_data, comm_result, error = self.packet_handler.read1ByteTxRx(motor_id, MODE_ADDR)
                
                if comm_result != scs.COMM_SUCCESS:
                    print(f"Failed to read mode for motor {motor_id}")
                    results[motor_id] = False
                    continue
                    
                # Switch to position mode if needed
                if mode_data != 0:
                    print(f"Motor {motor_id} is in mode {mode_data}, switching to position mode (0)...")
                    if not self.set_operating_mode(motor_id, 0):
                        print(f"Failed to switch motor {motor_id} to position mode")
                        results[motor_id] = False
                        continue
                        
                # Ensure torque is enabled
                torque_enabled, comm_result, error = self.packet_handler.read1ByteTxRx(motor_id, TORQUE_ENABLE_ADDR)
                if comm_result == scs.COMM_SUCCESS and torque_enabled != 1:
                    comm_result, error = self.packet_handler.write1ByteTxRx(motor_id, TORQUE_ENABLE_ADDR, 1)
                    if comm_result != scs.COMM_SUCCESS:
                        print(f"Warning: Failed to enable torque for motor {motor_id}")
                        
            except Exception as e:
                print(f"Error preparing motor {motor_id}: {e}")
                results[motor_id] = False
        
        # Clear any existing sync write parameters
        self.packet_handler.groupSyncWrite.clearParam()
        
        # Second pass: add parameters for sync write
        for motor_id, position in position_dict.items():
            if motor_id in results and results[motor_id] is False:
                continue  # Skip motors that failed in first pass
                
            try:
                # Validate position range
                if not (0 <= position <= 4095):
                    print(f"Warning: Position {position} out of range for motor {motor_id}. Clamping to [0, 4095]")
                    position = max(0, min(4095, position))
                
                # Get torque limit for this motor
                if self.servo_type == "hls" and torque_limit_dict and motor_id in torque_limit_dict:
                    torque_limit_normalized = torque_limit_dict[motor_id]
                    if not (0.0 <= torque_limit_normalized <= 1.0):
                        print(f"Warning: Torque limit {torque_limit_normalized} out of range for motor {motor_id}. Clamping to [0.0, 1.0]")
                        torque_limit_normalized = max(0.0, min(1.0, torque_limit_normalized))
                    
                    # Convert to 0-1000 range (0.1% units)
                    torque_value = int(torque_limit_normalized * 1000)
                elif self.servo_type == "hls":
                    # Default torque limit for HLS (100%)
                    torque_value = 1000
                
                # Add parameters using SyncWritePosEx
                if self.servo_type == "hls":
                    add_result = self.packet_handler.SyncWritePosEx(motor_id, position, speed, acceleration, torque_value)
                else:  # STS
                    add_result = self.packet_handler.SyncWritePosEx(motor_id, position, speed, acceleration)
                
                if not add_result:
                    print(f"Failed to add sync write parameters for motor {motor_id}")
                    results[motor_id] = False
                else:
                    results[motor_id] = True
                    
            except Exception as e:
                print(f"Error adding parameters for motor {motor_id}: {e}")
                results[motor_id] = False
        
        # Execute sync write
        comm_result = self.packet_handler.groupSyncWrite.txPacket()
        if comm_result != scs.COMM_SUCCESS:
            print(f"Sync write failed: {self.packet_handler.getTxRxResult(comm_result)}")
            # Mark all as failed if sync write failed
            for motor_id in position_dict.keys():
                if motor_id not in results:
                    results[motor_id] = False
        
        # Clear sync write parameters
        self.packet_handler.groupSyncWrite.clearParam()
        
        return results
    
    def disable_all_servos(self) -> None:
        """
        Disable torque on all configured servos.
        
        This ensures servos have no output and won't move.
        Safe to call even if not all servos are connected.
        """
        if not self._connected:
            return
            
        # Memory address for torque enable
        TORQUE_ENABLE_ADDR = 40  # Same for both STS and HLS
        
        print("\nDisabling all servos...")
        
        for motor_id in self.servo_ids:
            try:
                # Write 0 to disable torque
                comm_result, error = self.packet_handler.write1ByteTxRx(motor_id, TORQUE_ENABLE_ADDR, 0)
                
                if comm_result == scs.COMM_SUCCESS:
                    print(f"Motor {motor_id}: Disabled ✓")
                else:
                    print(f"Motor {motor_id}: Failed to disable - {self.packet_handler.getTxRxResult(comm_result)}")
                    
            except Exception as e:
                print(f"Motor {motor_id}: Error disabling - {e}")
                
        # Give servos time to process
        time.sleep(0.1)
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        # disconnect() will handle disabling servos
        self.disconnect()
        
    def __del__(self):
        """Destructor to ensure servos are disabled when object is destroyed."""
        try:
            # disconnect() will handle disabling servos
            self.disconnect()
        except:
            pass  # Ignore errors during cleanup