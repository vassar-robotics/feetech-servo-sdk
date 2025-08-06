# Vassar Feetech Servo SDK

A comprehensive Python SDK and command-line tool for controlling Feetech servos (STS/HLS series).

## Features

- 🔌 **Auto-detection** of serial ports
- 🎯 **Support for STS and HLS servos** (HLS includes torque control)
- 📖 **Read positions** from single or multiple servos  
- 🎯 **Set middle position** - Calibrate servos to position 2048
- ✍️ **Write position targets** (coming soon)
- 💪 **Write torque targets** (coming soon)
- 🚀 **High-performance** group sync operations
- 📊 **Real-time monitoring** with configurable update rates
- 🐍 **Clean Python API** with servo configuration at initialization
- 💻 **Command-line interface** for all operations
- 🔧 **Context manager support** for clean resource management

## Installation

### From PyPI

```bash
pip install vassar-feetech-servo-sdk
```

### From Source

```bash
git clone https://github.com/vassar-robotics/feetech-servo-sdk.git
cd feetech-servo-sdk
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

# Set all servos to middle position
vassar-servo --set-middle

# Read from specific motors at 60Hz
vassar-servo --motor-ids 1,3,5 --hz 60

# Use HLS servos (default is STS)
vassar-servo --servo-type hls

# Read once and exit
vassar-servo --once

# Output JSON format (useful for scripting)
vassar-servo --once --json
```

### Python API Usage

```python
from vassar_feetech_servo_sdk import ServoController

# Initialize controller with your servo configuration
servo_ids = [1, 2, 3, 4, 5, 6]
controller = ServoController(servo_ids=servo_ids, servo_type="sts")  # or "hls"
controller.connect()

# Read all configured servos
positions = controller.read_all_positions()
for motor_id, pos in positions.items():
    print(f"Motor {motor_id}: {pos} ({pos/4095*100:.1f}%)")

# Set servos to middle position
success = controller.set_middle_position()
if success:
    print("All servos calibrated to middle position!")

controller.disconnect()

# Using context manager
with ServoController([1, 2, 3], "sts") as controller:
    positions = controller.read_all_positions()
    print(positions)

# Continuous reading with callback
def my_callback(positions):
    print(f"Got positions: {positions}")

with ServoController([1, 2, 3], "hls") as controller:
    controller.read_positions_continuous(
        callback=my_callback,
        frequency=50.0
    )
```

### Advanced Usage

```python
# Initialize with specific configuration
controller = ServoController(
    servo_ids=[1, 2, 3, 4, 5, 6],
    servo_type="hls",  # 'sts' or 'hls'
    port="/dev/ttyUSB0",
    baudrate=1000000
)

# Error handling
from vassar_feetech_servo_sdk import ServoReaderError, PortNotFoundError

try:
    controller = ServoController([1, 2, 3], "sts")
    controller.connect()
    positions = controller.read_all_positions()
except PortNotFoundError:
    print("No servo port found!")
except ServoReaderError as e:
    print(f"Error: {e}")
```

## API Reference

### ServoController Class

#### Constructor

```python
ServoController(servo_ids, servo_type="sts", port=None, baudrate=1000000)
```

- `servo_ids`: List of servo IDs to control (e.g., [1, 2, 3, 4, 5, 6])
- `servo_type`: Type of servo - 'sts' or 'hls' (default: 'sts')
- `port`: Serial port path (auto-detect if None)
- `baudrate`: Communication speed (default: 1000000)

#### Methods

- `connect()`: Establish connection to servos
- `disconnect()`: Close connection
- `read_position(motor_id)`: Read single motor position
- `read_positions(motor_ids=None)`: Read multiple motor positions
- `read_all_positions()`: Read all configured servo positions
- `set_middle_position(motor_ids=None)`: Calibrate servos to middle position (2048)
- `read_positions_continuous(motor_ids=None, callback=None, frequency=30.0)`: Continuously read positions

### Utility Functions

- `find_servo_port()`: Auto-detect servo serial port

## Servo Types

- **STS**: Standard Feetech servos (default) - position and speed control
  - Middle position calibration uses torque=128 method
- **HLS**: High-end servos with additional torque control capabilities
  - Middle position calibration uses offset calibration (`reOfsCal`) method

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