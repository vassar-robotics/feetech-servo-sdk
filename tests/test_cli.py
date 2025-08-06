"""Tests for vassar_feetech_servo_sdk.cli module."""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys

from vassar_feetech_servo_sdk.cli import parse_motor_ids, main
from vassar_feetech_servo_sdk.exceptions import ServoReaderError, PortNotFoundError


class TestParseMotorIds:
    """Tests for parse_motor_ids function."""
    
    def test_parse_single_id(self):
        """Test parsing single motor ID."""
        result = parse_motor_ids("1")
        assert result == [1]
    
    def test_parse_multiple_ids(self):
        """Test parsing multiple motor IDs."""
        result = parse_motor_ids("1,2,3,4,5,6")
        assert result == [1, 2, 3, 4, 5, 6]
    
    def test_parse_with_spaces(self):
        """Test parsing with spaces."""
        result = parse_motor_ids(" 1 , 2 , 3 ")
        assert result == [1, 2, 3]
    
    def test_parse_invalid_format(self):
        """Test parsing invalid format."""
        with pytest.raises(ValueError, match="Invalid motor IDs format"):
            parse_motor_ids("1,a,3")
    
    def test_parse_empty_string(self):
        """Test parsing empty string."""
        with pytest.raises(ValueError, match="Invalid motor IDs format"):
            parse_motor_ids("")


class TestMainFunction:
    """Tests for main CLI function."""
    
    def setup_method(self):
        """Setup for each test."""
        self.original_argv = sys.argv.copy()
    
    def teardown_method(self):
        """Cleanup after each test."""
        sys.argv = self.original_argv
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    @patch('vassar_feetech_servo_sdk.cli.find_servo_port')
    def test_basic_continuous_reading(self, mock_find_port, mock_controller_class):
        """Test basic continuous reading mode."""
        # Setup
        sys.argv = ['vassar-servo']
        mock_find_port.return_value = '/dev/ttyUSB0'
        
        mock_controller = Mock()
        mock_controller.read_positions.side_effect = [
            {1: 1024, 2: 2048, 3: 3072},
            KeyboardInterrupt()  # Simulate user interrupt
        ]
        mock_controller_class.return_value = mock_controller
        
        # Capture output
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            with patch('sys.stderr', new=StringIO()) as mock_stderr:
                main()  # Should complete without SystemExit
        
        # Verify
        output = mock_stdout.getvalue()
        assert "Auto-detecting servo port..." in output
        assert "Found port: /dev/ttyUSB0" in output
        assert "Connecting to STS servos" in output
        assert "Reading at 30.0 Hz" in output
        
        mock_controller_class.assert_called_once_with(
            servo_ids=[1, 2, 3, 4, 5, 6],
            servo_type="sts",
            port="/dev/ttyUSB0",
            baudrate=1000000
        )
        mock_controller.connect.assert_called_once()
        mock_controller.disconnect.assert_called_once()
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_once_mode(self, mock_controller_class):
        """Test --once flag for single read."""
        # Setup
        sys.argv = ['vassar-servo', '--once', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.read_positions.return_value = {1: 2048, 2: 3072}
        mock_controller_class.return_value = mock_controller
        
        # Capture output
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            main()  # Should complete without SystemExit
        
        # Verify
        output = mock_stdout.getvalue()
        assert "Motor" in output
        assert "Position" in output
        assert "Percent" in output
        assert "2048" in output
        assert "3072" in output
        
        mock_controller.read_positions.assert_called_once()
        mock_controller.disconnect.assert_called_once()
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_json_mode(self, mock_controller_class):
        """Test --json flag for JSON output."""
        # Setup
        sys.argv = ['vassar-servo', '--once', '--json', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.read_positions.return_value = {1: 2048, 2: 3072}
        mock_controller_class.return_value = mock_controller
        
        # Capture output
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            main()  # Should complete without SystemExit
        
        # Verify
        output = mock_stdout.getvalue()
        
        # Should be valid JSON
        lines = output.strip().split('\n')
        json_output = None
        for line in lines:
            if line.startswith('{'):
                json_output = line
                break
        
        assert json_output is not None
        data = json.loads(json_output)
        assert data == {"1": 2048, "2": 3072}  # JSON keys are strings
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_set_middle_mode_success(self, mock_controller_class):
        """Test --set-middle flag for calibration."""
        # Setup
        sys.argv = ['vassar-servo', '--set-middle', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.set_middle_position.return_value = True
        mock_controller_class.return_value = mock_controller
        
        # Run
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Verify
        assert exc_info.value.code == 0
        mock_controller.set_middle_position.assert_called_once()
        mock_controller.disconnect.assert_called_once()
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_set_middle_mode_failure(self, mock_controller_class):
        """Test --set-middle flag when calibration fails."""
        # Setup
        sys.argv = ['vassar-servo', '--set-middle', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.set_middle_position.return_value = False
        mock_controller_class.return_value = mock_controller
        
        # Run
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        # Verify
        assert exc_info.value.code == 1
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_custom_motor_ids(self, mock_controller_class):
        """Test custom motor IDs."""
        # Setup
        sys.argv = ['vassar-servo', '--motor-ids', '2,4,6', '--once', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.read_positions.return_value = {2: 1024, 4: 2048, 6: 3072}
        mock_controller_class.return_value = mock_controller
        
        # Run
        main()  # Should complete without SystemExit
        
        # Verify
        mock_controller_class.assert_called_once_with(
            servo_ids=[2, 4, 6],
            servo_type="sts",
            port="/dev/ttyUSB0",
            baudrate=1000000
        )
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_hls_servo_type(self, mock_controller_class):
        """Test HLS servo type."""
        # Setup
        sys.argv = ['vassar-servo', '--servo-type', 'hls', '--once', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.read_positions.return_value = {1: 2048}
        mock_controller_class.return_value = mock_controller
        
        # Capture output
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            main()  # Should complete without SystemExit
        
        # Verify
        output = mock_stdout.getvalue()
        assert "Connecting to HLS servos" in output
        
        mock_controller_class.assert_called_once_with(
            servo_ids=[1, 2, 3, 4, 5, 6],
            servo_type="hls",
            port="/dev/ttyUSB0",
            baudrate=1000000
        )
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_custom_baudrate(self, mock_controller_class):
        """Test custom baudrate."""
        # Setup
        sys.argv = ['vassar-servo', '--baudrate', '115200', '--once', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.read_positions.return_value = {1: 2048}
        mock_controller_class.return_value = mock_controller
        
        # Run
        main()  # Should complete without SystemExit
        
        # Verify
        mock_controller_class.assert_called_once_with(
            servo_ids=[1, 2, 3, 4, 5, 6],
            servo_type="sts",
            port="/dev/ttyUSB0",
            baudrate=115200
        )
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_custom_frequency(self, mock_controller_class):
        """Test custom reading frequency."""
        # Setup
        sys.argv = ['vassar-servo', '--hz', '60', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        # Simulate immediate interrupt
        mock_controller.read_positions.side_effect = KeyboardInterrupt()
        mock_controller_class.return_value = mock_controller
        
        # Capture output
        with patch('sys.stdout', new=StringIO()) as mock_stdout:
            main()  # Should complete without SystemExit
        
        # Verify
        output = mock_stdout.getvalue()
        assert "Reading at 60.0 Hz" in output
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_invalid_motor_ids(self, mock_controller_class):
        """Test invalid motor IDs format."""
        # Setup
        sys.argv = ['vassar-servo', '--motor-ids', '1,invalid,3', '--port', '/dev/ttyUSB0']
        
        # Capture output
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Verify
        assert exc_info.value.code == 1
        error_output = mock_stderr.getvalue()
        assert "Invalid motor IDs format" in error_output
    
    @patch('vassar_feetech_servo_sdk.cli.find_servo_port')
    def test_port_not_found(self, mock_find_port):
        """Test when auto-detection fails to find port."""
        # Setup
        sys.argv = ['vassar-servo', '--once']
        mock_find_port.side_effect = PortNotFoundError("No suitable serial port found")
        
        # Capture output
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Verify
        assert exc_info.value.code == 1
        error_output = mock_stderr.getvalue()
        assert "No suitable serial port found" in error_output
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_servo_reader_error(self, mock_controller_class):
        """Test handling of ServoReaderError."""
        # Setup
        sys.argv = ['vassar-servo', '--once', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.connect.side_effect = ServoReaderError("Connection failed")
        mock_controller_class.return_value = mock_controller
        
        # Capture output
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Verify
        assert exc_info.value.code == 1
        error_output = mock_stderr.getvalue()
        assert "Connection failed" in error_output
        mock_controller.disconnect.assert_called_once()
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    def test_unexpected_error(self, mock_controller_class):
        """Test handling of unexpected errors."""
        # Setup
        sys.argv = ['vassar-servo', '--once', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.connect.side_effect = RuntimeError("Unexpected error")
        mock_controller_class.return_value = mock_controller
        
        # Capture output
        with patch('sys.stderr', new=StringIO()) as mock_stderr:
            with pytest.raises(SystemExit) as exc_info:
                main()
        
        # Verify
        assert exc_info.value.code == 1
        error_output = mock_stderr.getvalue()
        assert "Unexpected error" in error_output
        mock_controller.disconnect.assert_called_once()
    
    @patch('vassar_feetech_servo_sdk.cli.ServoController')
    @patch('vassar_feetech_servo_sdk.cli.time.sleep')
    @patch('vassar_feetech_servo_sdk.cli.time.perf_counter')
    def test_continuous_reading_timing(self, mock_perf_counter, mock_sleep, mock_controller_class):
        """Test continuous reading maintains proper timing."""
        # Setup
        sys.argv = ['vassar-servo', '--hz', '10', '--port', '/dev/ttyUSB0']
        
        mock_controller = Mock()
        mock_controller.read_positions.side_effect = [
            {1: 2048},
            {1: 2048},
            KeyboardInterrupt()
        ]
        mock_controller_class.return_value = mock_controller
        
        # Mock timing - simulate read taking 0.05 seconds
        mock_perf_counter.side_effect = [0.0, 0.05, 0.1, 0.15]
        
        # Run
        with patch('sys.stdout', new=StringIO()):
            try:
                main()
            except SystemExit:
                pass  # May exit on error, but shouldn't in this test
        
        # Verify timing
        # At 10Hz, loop time is 0.1s. If read took 0.05s, should sleep for 0.05s
        # Check that sleep was called with approximately 0.05s
        assert mock_sleep.called
        args, _ = mock_sleep.call_args
        assert abs(args[0] - 0.05) < 0.001  # Allow small floating point error