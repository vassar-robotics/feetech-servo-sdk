# Vassar Feetech Servo SDK - Package Structure

## Overview

The `vassar-feetech-servo-sdk` package bundles the `scservo_sdk` library directly, providing a complete solution for working with Feetech servos without requiring separate SDK installation.

## Directory Structure

```
vassar-feetech-servo-sdk/
├── scservo_sdk/                    # Bundled Feetech SDK (included in package)
│   ├── __init__.py
│   ├── port_handler.py             # Serial port handling
│   ├── protocol_packet_handler.py  # Protocol implementation
│   ├── sms_sts.py                  # SMS/STS servo support
│   ├── hls.py                      # HLS servo support
│   ├── scscl.py                    # SCSCL servo support
│   ├── group_sync_read.py          # Group sync reading
│   ├── group_sync_write.py         # Group sync writing
│   └── scservo_def.py              # Constants and definitions
│
├── vassar_feetech_servo_sdk/       # Main package
│   ├── __init__.py                 # Package exports
│   ├── reader.py                   # ServoReader class
│   ├── exceptions.py               # Custom exceptions
│   ├── cli.py                      # Command-line interface
│   └── __main__.py                 # Module execution
│
├── examples/                       # Example scripts
├── tests/                          # Unit tests
├── pyproject.toml                  # Package configuration
├── README.md                       # Documentation
└── LICENSE                         # MIT License
```

## Import Structure

### For Users

```python
# High-level API
from vassar_feetech_servo_sdk import ServoReader

# Direct SDK access (bundled)
import scservo_sdk as scs
```

### Internal Package Imports

The package uses the bundled `scservo_sdk` directly:

```python
# In reader.py
import scservo_sdk as scs
```

## Key Features

1. **Bundled SDK**: No separate `scservo-sdk` installation needed
2. **High-level API**: Easy-to-use `ServoReader` class
3. **CLI Tool**: `vassar-servo` command for quick testing
4. **Direct SDK Access**: Advanced users can still use `scservo_sdk` directly

## Installation

```bash
pip install vassar-feetech-servo-sdk
```

This installs both:
- The high-level `vassar_feetech_servo_sdk` package
- The bundled `scservo_sdk` library

## Usage Examples

### High-Level API
```python
from vassar_feetech_servo_sdk import ServoReader

with ServoReader() as reader:
    positions = reader.read_positions([1, 2, 3, 4, 5, 6])
```

### Direct SDK Access
```python
import scservo_sdk as scs

port_handler = scs.PortHandler('/dev/ttyUSB0')
packet_handler = scs.sms_sts(port_handler)
```

### Command Line
```bash
vassar-servo --motor-ids 1,2,3,4,5,6 --hz 30
```