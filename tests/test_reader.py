"""Tests for vassar_feetech_servo_sdk package."""

import pytest
from unittest.mock import Mock, patch
from vassar_feetech_servo_sdk import ServoController, find_servo_port, PortNotFoundError


class TestFindServoPort:
    """Tests for find_servo_port function."""
    
    @patch('serial.tools.list_ports.comports')
    def test_find_port_linux(self, mock_comports):
        """Test port finding on Linux."""
        mock_port = Mock()
        mock_port.device = '/dev/ttyUSB0'
        mock_comports.return_value = [mock_port]
        
        with patch('platform.system', return_value='Linux'):
            port = find_servo_port()
            assert port == '/dev/ttyUSB0'
    
    @patch('serial.tools.list_ports.comports')
    def test_find_port_macos(self, mock_comports):
        """Test port finding on macOS."""
        mock_port = Mock()
        mock_port.device = '/dev/tty.usbmodem123'
        mock_comports.return_value = [mock_port]
        
        with patch('platform.system', return_value='Darwin'):
            port = find_servo_port()
            assert port == '/dev/tty.usbmodem123'
    
    @patch('serial.tools.list_ports.comports')
    def test_find_port_windows(self, mock_comports):
        """Test port finding on Windows."""
        mock_port = Mock()
        mock_port.device = 'COM3'
        mock_comports.return_value = [mock_port]
        
        with patch('platform.system', return_value='Windows'):
            port = find_servo_port()
            assert port == 'COM3'
    
    @patch('serial.tools.list_ports.comports')
    def test_no_port_found(self, mock_comports):
        """Test exception when no port is found."""
        mock_comports.return_value = []
        
        with pytest.raises(PortNotFoundError):
            find_servo_port()


class TestServoController:
    """Tests for ServoController class."""
    
    def test_init_with_port(self):
        """Test initialization with specific port."""
        controller = ServoController(servo_ids=[1, 2, 3], servo_type='hls', port='/dev/ttyUSB0', baudrate=500000)
        assert controller.port == '/dev/ttyUSB0'
        assert controller.baudrate == 500000
        assert controller.servo_type == 'hls'
        assert controller.servo_ids == [1, 2, 3]
    
    @patch('vassar_feetech_servo_sdk.controller.find_servo_port')
    def test_init_auto_detect(self, mock_find_port):
        """Test initialization with auto-detected port."""
        mock_find_port.return_value = '/dev/ttyUSB0'
        controller = ServoController([1, 2, 3])
        assert controller.port == '/dev/ttyUSB0'
        assert controller.baudrate == 1000000
        assert controller.servo_type == 'sts'
    
    def test_servo_type_validation(self):
        """Test servo type validation."""
        # Valid types should work
        for servo_type in ['sts', 'hls']:
            controller = ServoController([1, 2, 3], servo_type=servo_type, port='/dev/test')
            assert controller.servo_type == servo_type
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with patch('vassar_feetech_servo_sdk.controller.scs.PortHandler'):
            controller = ServoController([1, 2, 3], port='/dev/test')
            # Mock the connection methods
            controller.connect = Mock()
            controller.disconnect = Mock()
            
            with controller as c:
                assert c is controller
                controller.connect.assert_called_once()
            
            controller.disconnect.assert_called_once()


# Add more tests as needed for:
# - Connection and disconnection
# - Reading positions
# - Error handling
# - Continuous reading
# etc.