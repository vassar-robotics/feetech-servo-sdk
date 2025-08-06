"""Tests for vassar_feetech_servo_sdk.controller module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from vassar_feetech_servo_sdk.controller import ServoController, find_servo_port
from vassar_feetech_servo_sdk.exceptions import PortNotFoundError, ConnectionError, CommunicationError


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
    
    def test_init_default(self):
        """Test initialization with defaults."""
        servo_ids = [1, 2, 3]
        controller = ServoController(servo_ids=servo_ids, port="/dev/ttyUSB0")
        
        assert controller.servo_ids == servo_ids
        assert controller.servo_type == "sts"
        assert controller.baudrate == 1000000
        assert controller.port_handler is None
        assert controller.packet_handler is None
        assert controller._connected is False
    
    def test_init_with_params(self):
        """Test initialization with custom parameters."""
        servo_ids = [4, 5, 6]
        controller = ServoController(
            servo_ids=servo_ids,
            servo_type="hls",
            port="/dev/ttyUSB1",
            baudrate=115200
        )
        
        assert controller.servo_ids == servo_ids
        assert controller.servo_type == "hls"
        assert controller.port == "/dev/ttyUSB1"
        assert controller.baudrate == 115200
    
    @patch('vassar_feetech_servo_sdk.controller.find_servo_port')
    def test_init_auto_port(self, mock_find_port):
        """Test initialization with automatic port detection."""
        mock_find_port.return_value = "/dev/ttyUSB0"
        controller = ServoController([1, 2])  # No port specified to trigger auto-detection
        
        assert controller.port == "/dev/ttyUSB0"
        mock_find_port.assert_called_once()
    
    def test_init_invalid_servo_type(self):
        """Test initialization with invalid servo type."""
        with pytest.raises(ValueError, match="Unsupported servo type"):
            ServoController([1, 2], servo_type="invalid", port="/dev/ttyUSB0")
    
    @patch('scservo_sdk.PortHandler')
    @patch('scservo_sdk.sms_sts')
    def test_connect_sts(self, mock_sms_sts, mock_port_handler):
        """Test connecting to STS servos."""
        # Setup mocks
        port_handler = Mock()
        port_handler.openPort.return_value = True
        port_handler.setBaudRate.return_value = True
        mock_port_handler.return_value = port_handler
        
        packet_handler = Mock()
        mock_sms_sts.return_value = packet_handler
        
        # Test connection
        controller = ServoController([1, 2], servo_type="sts", port="/dev/ttyUSB0")
        controller.connect()
        
        assert controller._connected is True
        assert controller.port_handler == port_handler
        assert controller.packet_handler == packet_handler
        mock_port_handler.assert_called_once_with("/dev/ttyUSB0")
        port_handler.openPort.assert_called_once()
        port_handler.setBaudRate.assert_called_once_with(1000000)
    
    @patch('scservo_sdk.PortHandler')
    @patch('scservo_sdk.hls')
    def test_connect_hls(self, mock_hls, mock_port_handler):
        """Test connecting to HLS servos."""
        # Setup mocks
        port_handler = Mock()
        port_handler.openPort.return_value = True
        port_handler.setBaudRate.return_value = True
        mock_port_handler.return_value = port_handler
        
        packet_handler = Mock()
        mock_hls.return_value = packet_handler
        
        # Test connection
        controller = ServoController([1, 2], servo_type="hls", port="/dev/ttyUSB0")
        controller.connect()
        
        assert controller._connected is True
        assert controller.packet_handler == packet_handler
        mock_hls.assert_called_once_with(port_handler)
    
    @patch('scservo_sdk.PortHandler')
    def test_connect_port_open_fail(self, mock_port_handler):
        """Test connection failure when port can't open."""
        port_handler = Mock()
        port_handler.openPort.return_value = False
        mock_port_handler.return_value = port_handler
        
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        with pytest.raises(ConnectionError, match="Failed to open port"):
            controller.connect()
    
    @patch('scservo_sdk.PortHandler')
    def test_connect_baudrate_fail(self, mock_port_handler):
        """Test connection failure when baudrate can't be set."""
        port_handler = Mock()
        port_handler.openPort.return_value = True
        port_handler.setBaudRate.return_value = False
        mock_port_handler.return_value = port_handler
        
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        with pytest.raises(ConnectionError, match="Failed to set baudrate"):
            controller.connect()
        
        port_handler.closePort.assert_called_once()
    
    def test_connect_already_connected(self):
        """Test connecting when already connected."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        controller._connected = True
        controller.connect()  # Should return immediately without error
    
    def test_disconnect(self):
        """Test disconnecting."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        controller._connected = True
        controller.port_handler = Mock()
        
        controller.disconnect()
        
        assert controller._connected is False
        controller.port_handler.closePort.assert_called_once()
    
    def test_disconnect_not_connected(self):
        """Test disconnecting when not connected."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        controller.disconnect()  # Should not raise error
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    def test_read_position_success(self):
        """Test reading position from single motor."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        controller.packet_handler.ReadPos.return_value = (2048, 0, 0)
        controller.packet_handler.getTxRxResult.return_value = "Success"
        controller.packet_handler.getRxPacketError.return_value = "No error"
        
        position = controller.read_position(1)
        
        assert position == 2048
        controller.packet_handler.ReadPos.assert_called_once_with(1)
    
    def test_read_position_not_connected(self):
        """Test reading position when not connected."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        
        with pytest.raises(ConnectionError, match="Not connected"):
            controller.read_position(1)
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    def test_read_position_comm_error(self):
        """Test reading position with communication error."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        controller.packet_handler.ReadPos.return_value = (0, 1, 0)  # comm_result != COMM_SUCCESS
        controller.packet_handler.getTxRxResult.return_value = "Timeout"
        
        with pytest.raises(CommunicationError, match="Failed to read position"):
            controller.read_position(1)
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    def test_read_position_packet_error(self):
        """Test reading position with packet error."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        controller.packet_handler.ReadPos.return_value = (0, 0, 1)  # error != 0
        controller.packet_handler.getRxPacketError.return_value = "Checksum error"
        
        with pytest.raises(CommunicationError, match="Motor 1 error"):
            controller.read_position(1)
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    @patch('scservo_sdk.GroupSyncRead')
    def test_read_positions_success(self, mock_group_sync_read):
        """Test reading positions from multiple motors."""
        # Setup mocks
        group_sync = Mock()
        group_sync.addParam.side_effect = [True, True, True]
        group_sync.txRxPacket.return_value = 0
        group_sync.isAvailable.side_effect = [(True, 0), (True, 0), (True, 0)]
        group_sync.getData.side_effect = [1024, 2048, 3072]
        mock_group_sync_read.return_value = group_sync
        
        controller = ServoController([1, 2, 3], port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        controller.packet_handler.getTxRxResult.return_value = "Success"
        
        positions = controller.read_positions([1, 2, 3])
        
        assert positions == {1: 1024, 2: 2048, 3: 3072}
        assert group_sync.addParam.call_count == 3
        group_sync.txRxPacket.assert_called_once()
        group_sync.clearParam.assert_called_once()
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    @patch('scservo_sdk.GroupSyncRead')
    def test_read_positions_default_ids(self, mock_group_sync_read):
        """Test reading positions with default motor IDs."""
        group_sync = Mock()
        group_sync.addParam.return_value = True
        group_sync.txRxPacket.return_value = 0
        group_sync.isAvailable.return_value = (True, 0)
        group_sync.getData.return_value = 2048
        mock_group_sync_read.return_value = group_sync
        
        controller = ServoController([5, 6], port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        
        positions = controller.read_positions()  # Should use self.servo_ids
        
        assert len(positions) == 2
        assert 5 in positions
        assert 6 in positions
    
    def test_read_positions_not_connected(self):
        """Test reading positions when not connected."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        
        with pytest.raises(ConnectionError, match="Not connected"):
            controller.read_positions()
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    @patch('scservo_sdk.GroupSyncRead')
    def test_read_all_positions(self, mock_group_sync_read):
        """Test reading all configured positions."""
        group_sync = Mock()
        group_sync.addParam.return_value = True
        group_sync.txRxPacket.return_value = 0
        group_sync.isAvailable.return_value = (True, 0)
        group_sync.getData.return_value = 2048
        mock_group_sync_read.return_value = group_sync
        
        controller = ServoController([1, 2, 3], port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        
        positions = controller.read_all_positions()
        
        assert len(positions) == 3
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    @patch('scservo_sdk.GroupSyncWrite')
    @patch('vassar_feetech_servo_sdk.controller.time.sleep')
    def test_set_middle_position_sts_success(self, mock_sleep, mock_group_sync_write):
        """Test setting middle position for STS servos."""
        # Setup mocks
        group_sync = Mock()
        group_sync.addParam.side_effect = [True, True]
        group_sync.txPacket.return_value = 0
        mock_group_sync_write.return_value = group_sync
        
        controller = ServoController([1, 2], servo_type="sts", port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        
        # Mock read_positions to return values close to 2048
        with patch.object(controller, 'read_positions', return_value={1: 2045, 2: 2050}):
            success = controller.set_middle_position()
        
        assert success is True
        mock_group_sync_write.assert_called_once_with(controller.packet_handler, 40, 1)
        assert group_sync.addParam.call_count == 2
        group_sync.addParam.assert_any_call(1, [128])
        group_sync.addParam.assert_any_call(2, [128])
        group_sync.txPacket.assert_called_once()
        group_sync.clearParam.assert_called_once()
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    @patch('vassar_feetech_servo_sdk.controller.time.sleep')
    def test_set_middle_position_hls_success(self, mock_sleep):
        """Test setting middle position for HLS servos."""
        controller = ServoController([1, 2], servo_type="hls", port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        controller.packet_handler.reOfsCal.side_effect = [(0, 0), (0, 0)]
        controller.packet_handler.getTxRxResult.return_value = "Success"
        controller.packet_handler.getRxPacketError.return_value = "No error"
        
        # Mock read_positions to return values close to 2048
        with patch.object(controller, 'read_positions', return_value={1: 2045, 2: 2050}):
            success = controller.set_middle_position()
        
        assert success is True
        assert controller.packet_handler.reOfsCal.call_count == 2
        controller.packet_handler.reOfsCal.assert_any_call(1, 2048)
        controller.packet_handler.reOfsCal.assert_any_call(2, 2048)
    
    def test_set_middle_position_not_connected(self):
        """Test setting middle position when not connected."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        
        with pytest.raises(ConnectionError, match="Not connected"):
            controller.set_middle_position()
    
    @patch('scservo_sdk.COMM_SUCCESS', 0)
    @patch('vassar_feetech_servo_sdk.controller.time.sleep')
    def test_set_middle_position_hls_failure(self, mock_sleep):
        """Test setting middle position failure for HLS servos."""
        controller = ServoController([1, 2], servo_type="hls", port="/dev/ttyUSB0")
        controller._connected = True
        controller.packet_handler = Mock()
        controller.packet_handler.reOfsCal.side_effect = [(1, 0), (0, 0)]  # First motor fails
        controller.packet_handler.getTxRxResult.return_value = "Timeout"
        
        with pytest.raises(CommunicationError, match="Failed to calibrate some HLS servos"):
            controller.set_middle_position()
    
    def test_context_manager(self):
        """Test context manager functionality."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        
        with patch.object(controller, 'connect') as mock_connect:
            with patch.object(controller, 'disconnect') as mock_disconnect:
                with controller as ctx:
                    assert ctx is controller
                    mock_connect.assert_called_once()
                
                mock_disconnect.assert_called_once()
    
    def test_context_manager_with_exception(self):
        """Test context manager cleanup on exception."""
        controller = ServoController([1, 2], port="/dev/ttyUSB0")
        
        with patch.object(controller, 'connect'):
            with patch.object(controller, 'disconnect') as mock_disconnect:
                try:
                    with controller:
                        raise ValueError("Test error")
                except ValueError:
                    pass
                
                mock_disconnect.assert_called_once()