# STS Series Servo Memory Table

**Note**: This is an example template. Replace with actual Feetech memory table data.

## EEPROM Area (Non-volatile Memory)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 0 (0x00) | Model Number L | R | 1 | - | - | Lower byte of model number |
| 1 (0x01) | Model Number H | R | 1 | - | - | Upper byte of model number |
| 3 (0x03) | Firmware Version | R | 1 | - | - | Firmware version information |
| 4 (0x04) | ID | RW | 1 | 1 | 0-253 | Servo ID (254=broadcast) |
| 5 (0x05) | Baud Rate | RW | 1 | 1 | 0-7 | Communication baud rate |
| 6 (0x06) | Return Delay Time | RW | 1 | 0 | 0-254 | Response delay (2μs units) |
| 11 (0x0B) | Max Temperature | RW | 1 | 80 | 0-100 | Maximum operating temperature (°C) |
| 12 (0x0C) | Max Voltage | RW | 1 | 140 | 50-250 | Maximum voltage limit (0.1V units) |
| 13 (0x0D) | Min Voltage | RW | 1 | 60 | 50-250 | Minimum voltage limit (0.1V units) |

## RAM Area (Volatile Memory)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 40 (0x28) | Torque Enable | RW | 1 | 0 | 0-1,128 | 0=off, 1=on, 128=calibrate middle |
| 41 (0x29) | LED | RW | 1 | 0 | 0-7 | LED control (bit flags) |
| 42 (0x2A) | Goal Position L | RW | 1 | - | 0-255 | Target position lower byte |
| 43 (0x2B) | Goal Position H | RW | 1 | - | 0-15 | Target position upper byte |
| 44 (0x2C) | Goal Time L | RW | 1 | 0 | 0-255 | Movement time lower byte |
| 45 (0x2D) | Goal Time H | RW | 1 | 0 | 0-255 | Movement time upper byte |
| 46 (0x2E) | Goal Speed L | RW | 1 | 0 | 0-255 | Target speed lower byte |
| 47 (0x2F) | Goal Speed H | RW | 1 | 0 | 0-15 | Target speed upper byte |
| 56 (0x38) | Present Position L | R | 1 | - | 0-255 | Current position lower byte |
| 57 (0x39) | Present Position H | R | 1 | - | 0-15 | Current position upper byte |
| 58 (0x3A) | Present Speed L | R | 1 | - | 0-255 | Current speed lower byte |
| 59 (0x3B) | Present Speed H | R | 1 | - | 0-255 | Current speed upper byte |
| 60 (0x3C) | Present Load L | R | 1 | - | 0-255 | Current load lower byte |
| 61 (0x3D) | Present Load H | R | 1 | - | 0-10 | Current load upper byte |
| 62 (0x3E) | Present Voltage | R | 1 | - | 50-250 | Current voltage (0.1V units) |
| 63 (0x3F) | Present Temperature | R | 1 | - | 0-100 | Current temperature (°C) |

## Special Commands

| Value | Written to Address | Effect |
|-------|-------------------|---------|
| 128 | Torque Enable (0x28) | Calibrates current position as middle position (2048) |

## Notes for AI Agents

1. **Position Values**: 12-bit values (0-4095), stored as two bytes (L and H)
2. **Goal Time**: Used in STS servos to control movement duration
3. **Memory Types**: EEPROM values persist after power off, RAM values reset
4. **Write Operations**: Always check access permissions before writing