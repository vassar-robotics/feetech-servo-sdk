# Feetech Servo SDK

A lightweight Python SDK for controlling Feetech servo motors (STS/SCS series).

## Features

- 🚀 **Simple and minimal** - Core functionality in < 100 lines
- 📡 **Auto port detection** - Automatically finds connected servos
- 🎯 **Easy calibration** - One-line command to set middle position
- 📊 **Real-time monitoring** - Read servo positions at high frequency
- 🔧 **Low-level access** - Direct register read/write capabilities

## Installation

### Prerequisites

```bash
pip install pyserial
```

### Quick Start

1. Clone this repository:
```bash
git clone https://github.com/vassar-robotics/feetech-servo-sdk.git
cd feetech-servo-sdk
```

2. Run examples:
```bash
# Read servo positions
python examples/read_positions.py

# Calibrate to middle position
python examples/calibrate_middle_position.py
```

## Examples

### Reading Servo Positions

```python
import scservo_sdk as scs
from feetech_utils import find_port, read_positions

# Auto-detect port
port = find_port()

# Connect
port_handler = scs.PortHandler(port)
packet_handler = scs.PacketHandler(0)
port_handler.openPort()
port_handler.setBaudRate(1000000)

# Read positions
motor_ids = [1, 2, 3, 4, 5, 6]
positions = read_positions(port_handler, packet_handler, motor_ids)
print(positions)  # {1: 2048, 2: 2048, ...}
```

### Calibrating Middle Position

The SDK provides a simple calibration method using Feetech's built-in command:

```python
# Write 128 to address 40 (TORQUE_ENABLE) to calibrate to position 2048
packet_handler.write1ByteTxRx(port_handler, motor_id, 40, 128)
```

This instantly calibrates the current physical position to read as 2048.

## Supported Servos

- STS3215
- Other STS/SCS series servos (may require minor modifications)

## Register Reference

Common register addresses for Feetech servos:

| Address | Name | Description |
|---------|------|-------------|
| 40 (0x28) | TORQUE_ENABLE | Write 128 to calibrate to 2048 |
| 56 (0x38) | PRESENT_POSITION | Current position (read-only) |
| 31 (0x1F) | HOMING_OFFSET | Position offset calibration |
| 55 (0x37) | LOCK_FLAG | 0=save to EEPROM, 1=don't save |

## Documentation

- [Official Feetech Manual](http://doc.feetech.cn/#/prodinfodownload?srcType=FT-SMS-STS-emanual-229f4476422d4059abfb1cb0)
- [Example Scripts](examples/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see LICENSE file for details.

## Acknowledgments

Based on work from the Vassar Robotics team's LeRobot project.