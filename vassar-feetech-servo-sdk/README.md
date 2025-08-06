# Vassar Feetech Servo SDK

A Python library and command-line tool for reading positions from Feetech servos (STS/SMS/HLS series).

## Features

- 🔌 **Auto-detection** of serial ports
- 🎯 **Support for multiple servo types**: STS, SMS, and HLS series
- 🚀 **High-performance** group sync read for multiple servos
- 📊 **Real-time display** with configurable update rates
- 🐍 **Simple Python API** for integration into your projects
- 💻 **Command-line interface** for quick testing and monitoring
- 🔧 **Context manager support** for clean resource management

## Installation

### From PyPI (when published)

```bash
pip install vassar-feetech-servo-sdk
```

### From Source

```bash
git clone https://github.com/yourusername/vassar-feetech-servo-sdk.git
cd vassar-feetech-servo-sdk
pip install -e .
```

## Dependencies

- Python >= 3.7
- pyserial >= 3.5

Note: The `scservo_sdk` is bundled with this package, so no separate installation is needed.

## Quick Start

### Command Line Usage

```bash
# Read from motors 1-6 continuously at 30Hz
vassar-servo

# Read from specific motors at 60Hz
vassar-servo --motor-ids 1,3,5 --hz 60

# Use specific port and servo type
vassar-servo --port /dev/ttyUSB0 --servo-type hls

# Read once and exit
vassar-servo --once

# Output JSON format (useful for scripting)
vassar-servo --once --json
```

### Python API Usage

```python
from vassar_feetech_servo_sdk import ServoReader

# Basic usage
reader = ServoReader()  # Auto-detect port, SMS/STS servos
reader.connect()

# Read single motor
position = reader.read_position(motor_id=1)
print(f"Motor 1 position: {position}")

# Read multiple motors
positions = reader.read_positions([1, 2, 3, 4, 5, 6])
for motor_id, pos in positions.items():
    print(f"Motor {motor_id}: {pos} ({pos/4095*100:.1f}%)")

reader.disconnect()

# Using context manager
with ServoReader() as reader:
    positions = reader.read_positions([1, 2, 3])
    print(positions)

# Continuous reading with callback
def my_callback(positions):
    print(f"Got positions: {positions}")

with ServoReader() as reader:
    reader.read_positions_continuous(
        motor_ids=[1, 2, 3],
        callback=my_callback,
        frequency=50.0
    )
```

### Advanced Usage

```python
# Specify port and servo type
reader = ServoReader(
    port="/dev/ttyUSB0",
    baudrate=1000000,
    servo_type="hls"  # 'sms_sts', 'hls', or 'scscl'
)

# Error handling
from vassar_feetech_servo_sdk import ServoReaderError, PortNotFoundError

try:
    reader = ServoReader()
    reader.connect()
    position = reader.read_position(1)
except PortNotFoundError:
    print("No servo port found!")
except ServoReaderError as e:
    print(f"Error: {e}")
```

## API Reference

### ServoReader Class

#### Constructor

```python
ServoReader(port=None, baudrate=1000000, servo_type="sms_sts")
```

- `port`: Serial port path (auto-detect if None)
- `baudrate`: Communication speed (default: 1000000)
- `servo_type`: Type of servo - 'sms_sts', 'hls', or 'scscl'

#### Methods

- `connect()`: Establish connection to servos
- `disconnect()`: Close connection
- `read_position(motor_id)`: Read single motor position
- `read_positions(motor_ids)`: Read multiple motor positions
- `read_positions_continuous(motor_ids, callback=None, frequency=30.0)`: Continuously read positions

### Utility Functions

- `find_servo_port()`: Auto-detect servo serial port

## Servo Types

- **SMS/STS**: Most common Feetech servos (default)
- **HLS**: High-end servos with torque control
- **SCSCL**: Specialized servo series

## Troubleshooting

### Port Not Found

If auto-detection fails, specify the port manually:

```bash
# Linux
vassar-servo --port /dev/ttyUSB0

# macOS
vassar-servo --port /dev/tty.usbserial-*

# Windows
vassar-servo --port COM3
```

### Permission Denied (Linux)

Add your user to the dialout group:

```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

### Connection Failed

1. Check servo power supply
2. Verify baudrate matches servo configuration (default: 1000000)
3. Ensure proper wiring (TX/RX not swapped)

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/vassar-feetech-servo-sdk.git
cd vassar-feetech-servo-sdk

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black feetech_reader

# Type checking
mypy feetech_reader
```

### Building and Publishing

```bash
# Build package
python -m build

# Test upload to TestPyPI
twine upload --repository testpypi dist/*

# Upload to PyPI
twine upload dist/*
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Advanced Usage - Direct scservo_sdk Access

The `scservo_sdk` is bundled with this package. For advanced users who need direct access to the low-level SDK:

```python
import scservo_sdk as scs

# Direct SDK usage
port_handler = scs.PortHandler('/dev/ttyUSB0')
packet_handler = scs.sms_sts(port_handler)  # or scs.hls() for HLS servos

# ... use the SDK directly
```

## Acknowledgments

Built on top of the excellent `scservo_sdk` library for Feetech servo communication.