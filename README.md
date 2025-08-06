# Vassar Feetech Servo SDK

[![PyPI version](https://badge.fury.io/py/vassar-feetech-servo-sdk.svg)](https://badge.fury.io/py/vassar-feetech-servo-sdk)
[![Stability: Stable](https://img.shields.io/badge/stability-stable-green.svg)](https://github.com/vassar-robotics/feetech-servo-sdk)
[![No Breaking Changes](https://img.shields.io/badge/breaking%20changes-none-brightgreen)](https://github.com/vassar-robotics/feetech-servo-sdk)

A comprehensive Python SDK for controlling Feetech servos (STS/HLS series).

## Features

- 🔌 **Auto-detection** of serial ports
- 🎯 **Support for STS and HLS servos** (HLS includes torque control)
- 📖 **Read positions** from single or multiple servos  
- 🎯 **Set middle position** - Calibrate servos to position 2048
- 💪 **Write torque targets** - HLS servos only with automatic mode switching
- 🔧 **Set operating modes** - Configure servo behavior (position/speed/torque/PWM)

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
```

### Changing Servo IDs

```python
from vassar_feetech_servo_sdk import ServoController

# Connect to a servo with current ID 1
controller = ServoController(servo_ids=[1], servo_type="sts")
controller.connect()

# Change its ID from 1 to 10
success = controller.set_motor_id(
    current_id=1,
    new_id=10,
    confirm=True  # Will ask for user confirmation
)

if success:
    print("ID changed! Power cycle the servo to apply.")
    
controller.disconnect()

# After power cycling, connect with new ID
controller = ServoController(servo_ids=[10], servo_type="sts")
controller.connect()
```

### Torque Control (HLS Only)

```python
from vassar_feetech_servo_sdk import ServoController

# Connect to HLS servos
controller = ServoController(servo_ids=[1, 2, 3], servo_type="hls")
controller.connect()

# Write torque values (automatically switches to torque mode)
torque_values = {
    1: 500,   # 500 * 6.5mA = 3.25A forward
    2: -300,  # 300 * 6.5mA = 1.95A reverse  
    3: 0      # No torque
}

results = controller.write_torque(torque_values)
print(f"Torque write results: {results}")

# You can also manually set operating modes
controller.set_operating_mode(1, 0)  # Position mode
controller.set_operating_mode(2, 1)  # Speed mode
controller.set_operating_mode(3, 2)  # Torque mode

controller.disconnect()
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
- `set_motor_id(current_id, new_id, confirm=True)`: Change a servo's ID (requires power cycle)
- `set_operating_mode(motor_id, mode)`: Set servo operating mode (0-3)
- `write_torque(torque_dict)`: Write torque values to HLS servos (auto-switches to torque mode)

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

```python
# Linux
controller = ServoController(servo_ids=[1,2,3], port="/dev/ttyUSB0")

# macOS
controller = ServoController(servo_ids=[1,2,3], port="/dev/tty.usbserial-XXXXX")

# Windows
controller = ServoController(servo_ids=[1,2,3], port="COM3")
```

### Permission Denied (Linux)

Option 1: Add your user to the dialout group (recommended):

```bash
sudo usermod -a -G dialout $USER
# Log out and back in for changes to take effect
```

Option 2: Grant permissions to the serial port (temporary):

```bash
sudo chmod 666 /dev/ttyUSB0
# Replace /dev/ttyUSB0 with your actual serial port
```

### Connection Failed

1. Check servo power supply
2. Verify baudrate matches servo configuration (default: 1000000)
3. Ensure proper wiring (TX/RX not swapped)

## Examples

The package includes several example scripts in the `examples/` directory:

- `basic_usage.py` - Simple example showing how to connect and read servo positions
- `continuous_reading.py` - Real-time monitoring with custom callbacks
- `servo_types.py` - Demonstrates differences between STS and HLS servos
- `set_middle_position.py` - Shows how to calibrate servos to middle position

## Testing

Run the test suite:

```bash
./run_tests.sh  # Installs dev dependencies and runs tests with coverage
# or
pip install -r requirements-dev.txt
python -m pytest tests/ -v
```

## Acknowledgments

Built on top of the excellent `scservo_sdk` library for Feetech servo communication.