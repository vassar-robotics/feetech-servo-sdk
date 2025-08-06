"""Tests for vassar_feetech_servo_sdk package."""

import pytest
from unittest.mock import Mock, patch
from vassar_feetech_servo_sdk import ServoReader, find_servo_port, PortNotFoundError


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


class TestServoReader:
    """Tests for ServoReader class."""
    
    def test_init_with_port(self):
        """Test initialization with specific port."""
        reader = ServoReader(port='/dev/ttyUSB0', baudrate=500000, servo_type='hls')
        assert reader.port == '/dev/ttyUSB0'
        assert reader.baudrate == 500000
        assert reader.servo_type == 'hls'
    
    @patch('vassar_feetech_servo_sdk.reader.find_servo_port')
    def test_init_auto_detect(self, mock_find_port):
        """Test initialization with auto-detected port."""
        mock_find_port.return_value = '/dev/ttyUSB0'
        reader = ServoReader()
        assert reader.port == '/dev/ttyUSB0'
        assert reader.baudrate == 1000000
        assert reader.servo_type == 'sms_sts'
    
    def test_servo_type_validation(self):
        """Test servo type validation."""
        # Valid types should work
        for servo_type in ['sms_sts', 'hls', 'scscl']:
            reader = ServoReader(port='/dev/test', servo_type=servo_type)
            assert reader.servo_type == servo_type
    
    def test_context_manager(self):
        """Test context manager functionality."""
        with patch('vassar_feetech_servo_sdk.reader.scs.PortHandler'):
            reader = ServoReader(port='/dev/test')
            # Mock the connection methods
            reader.connect = Mock()
            reader.disconnect = Mock()
            
            with reader as r:
                assert r is reader
                reader.connect.assert_called_once()
            
            reader.disconnect.assert_called_once()


# Add more tests as needed for:
# - Connection and disconnection
# - Reading positions
# - Error handling
# - Continuous reading
# etc.