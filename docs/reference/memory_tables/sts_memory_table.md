# STS Series Servo Memory Table

STS/SMS servos use the FT-SCS custom protocol. Default serial configuration: 8 data bits, no parity, 1 stop bit.
- **STS**: Default baud rate 1Mbps, TTL single bus
- **SMS**: Default baud rate 115.2Kbps, RS485 bus

## Version Information (Read-only)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 0 (0x00) | Firmware Major Version | R | 1 | - | - | Main firmware version |
| 1 (0x01) | Firmware Minor Version | R | 1 | - | - | Sub firmware version |
| 2 (0x02) | Endianness | R | 1 | 0 | - | 0=little-endian storage |
| 3 (0x03) | Servo Major Version | R | 1 | - | - | Main servo version |
| 4 (0x04) | Servo Minor Version | R | 1 | - | - | Sub servo version |

## EEPROM Configuration (Non-volatile)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 5 (0x05) | ID | RW | 1 | 1 | 0-253 | Unique ID on bus |
| 6 (0x06) | Baud Rate | RW | 1 | 0 | 0-7 | 0=1M, 1=500K, 2=250K, 3=128K, 4=115.2K, 5=76.8K, 6=57.6K, 7=38.4K |
| 7 (0x07) | Return Delay Time | RW | 1 | 0 | 0, 50-253 | Response delay (2μs/unit). <50 defaults to 50 (100μs). Not functional on STS |
| 8 (0x08) | Response Level | RW | 1 | 1 | 0-1 | 0=read/ping only, 1=all commands |
| 9 (0x09) | Min Angle Limit | RW | 2 | 0 | 0-4094 | Min position (0.087°/unit). 0 for multi-turn |
| 11 (0x0B) | Max Angle Limit | RW | 2 | 4095 | 1-4095 | Max position (0.087°/unit). 0 for multi-turn |
| 13 (0x0D) | Max Temperature | RW | 1 | 70 | 0-100 | Maximum temperature limit (°C) |
| 14 (0x0E) | Max Voltage | RW | 1 | - | 0-254 | Maximum voltage (0.1V/unit) |
| 15 (0x0F) | Min Voltage | RW | 1 | 40 | 0-254 | Minimum voltage (0.1V/unit) |
| 16 (0x10) | Max Torque | RW | 2 | 1000 | 0-1000 | Max torque (0.1%). Loaded to addr 48 on startup |
| 18 (0x12) | Phase | RW | 1 | - | 0-254 | Special function byte - do not modify |
| 19 (0x13) | Unload Conditions | RW | 1 | - | 0-254 | Protection enable bits (1=enable, 0=disable) |
| 20 (0x14) | LED Alarm Conditions | RW | 1 | - | 0-254 | LED alarm enable bits (1=enable, 0=disable) |
| 21 (0x15) | Position P Gain | RW | 1 | - | 0-254 | Position loop P coefficient |
| 22 (0x16) | Position D Gain | RW | 1 | - | 0-254 | Position loop D coefficient |
| 23 (0x17) | Position I Gain | RW | 1 | 0 | 0-254 | Position loop I coefficient |
| 24 (0x18) | Min Starting Force | RW | 1 | - | 0-254 | Minimum startup torque (0.1%) |
| 25 (0x19) | Integral Limit | RW | 1 | 0 | 0-254 | Max integral = value×4. 0=no limit. Modes 0,4 |
| 26 (0x1A) | CW Dead Zone | RW | 1 | 1 | 0-16 | Clockwise dead zone (0.087°/unit) |
| 27 (0x1B) | CCW Dead Zone | RW | 1 | 1 | 0-16 | Counter-clockwise dead zone (0.087°/unit) |
| 28 (0x1C) | Protection Current | RW | 2 | 511 | 0-2047 | Current limit (6.5mA/unit) |
| 30 (0x1E) | Angle Resolution | RW | 1 | 1 | 1-128 | Sensor resolution multiplier |
| 31 (0x1F) | Position Offset | RW | 2 | 0 | 0-8191 | Position offset (0.087°/unit), complex encoding |
| 33 (0x21) | Operating Mode | RW | 1 | 0 | 0-3 | 0=Position, 1=Speed, 2=PWM, 3=Step |
| 34 (0x22) | Holding Torque | RW | 1 | 20 | 0-254 | Torque (1%) after overload protection triggers |
| 35 (0x23) | Protection Time | RW | 1 | 200 | 0-254 | Overload time duration (10ms/unit) |
| 36 (0x24) | Overload Torque | RW | 1 | 80 | 0-254 | Overload torque threshold (1%) |
| 37 (0x25) | Speed P Gain | RW | 1 | - | 0-254 | Speed loop P coefficient (Mode 1) |
| 38 (0x26) | Overcurrent Time | RW | 1 | 200 | 0-254 | Overcurrent protection time (10ms/unit) |
| 39 (0x27) | Speed I Gain | RW | 1 | - | 0-254 | Speed loop I coefficient (Mode 1) |

## SRAM Control (Volatile)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 40 (0x28) | Torque Enable | RW | 1 | 0 | 0-2,128 | 0=off, 1=on, 2=damping, 128=calibrate middle |
| 41 (0x29) | Acceleration | RW | 1 | 0 | 0-254 | Acceleration (8.7°/s²/unit). 0=max acceleration |
| 42 (0x2A) | Goal Position | RW | 2 | 0 | -32767 to 32767 | Target position (0.087°/unit). BIT15=direction |
| 44 (0x2C) | PWM Speed | RW | 2 | 1000 | 0-1000 | Speed in PWM mode (0.1%). BIT10=direction |
| 46 (0x2E) | Goal Speed | RW | 2 | Factory max | -32767 to 32767 | Max speed. Unit set by Phase. 0=max/stop. BIT15=direction |
| 48 (0x30) | Torque Limit | RW | 2 | From addr 16 | 0-1000 | Stall torque limit (0.1%) |
| 55 (0x37) | Lock Flag | RW | 1 | 1 | 0-1 | 0=save EEPROM changes, 1=don't save |

## SRAM Feedback (Read-only)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 56 (0x38) | Present Position | R | 2 | - | - | Current position (0.087°/unit). BIT15=direction |
| 58 (0x3A) | Present Speed | R | 2 | - | - | Current speed. Unit set by Phase. BIT15=direction |
| 60 (0x3C) | Present Load | R | 2 | - | - | Current PWM duty (0.1%). BIT10=direction |
| 62 (0x3E) | Present Voltage | R | 1 | - | - | Current voltage (0.1V/unit) |
| 63 (0x3F) | Present Temperature | R | 1 | - | - | Current temperature (°C) |
| 64 (0x40) | Async Write Flag | R | 1 | 0 | - | Flag for async write operations |
| 65 (0x41) | Status | R | 1 | 0 | - | Error flags (see Status Bits section) |
| 66 (0x42) | Moving Flag | R | 1 | 0 | - | 1=moving, 0=stopped/at target |
| 67 (0x43) | Target Position | R | 2 | 0 | - | Current target position (0.087°/unit) |
| 69 (0x45) | Present Current | R | 2 | - | - | Motor phase current (6.5mA/unit) |

## Factory Parameters (Read-only)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 80 (0x50) | Speed Threshold | R | 1 | - | - | Movement speed threshold |
| 81 (0x51) | DTs(ms) | R | 1 | - | - | Factory parameter |
| 82 (0x52) | Speed Unit Coeff | R | 1 | - | - | Speed unit coefficient |
| 83 (0x53) | Hts(ns) | R | 1 | - | - | 20.83ns. Valid for SMS fw>=2.54 |
| 84 (0x54) | Max Speed Limit | R | 1 | - | - | Maximum speed limit (0.732RPM/unit) |
| 85 (0x55) | Acceleration Limit | R | 1 | - | - | Acceleration limit |
| 86 (0x56) | Accel Multiplier | R | 1 | - | - | Multiplier when acceleration is 0 |

## Special Byte Explanations

### Phase Byte (Address 18/0x12)

| Bit | Weight | Description |
|-----|--------|-------------|
| BIT0 | 1 | Drive phase: 0=normal, 1=reverse |
| BIT1 | 2 | Drive bridge mode: 0=brushless, 1=brushed |
| BIT2 | 4 | Speed unit: 0=0.732RPM, 1=0.0146RPM |
| BIT3 | 8 | Speed mode: 0=speed 0 is stop, 1=speed 0 is max |
| BIT4 | 16 | Angle feedback mode: 0=single turn, 1=multi-turn |
| BIT5 | 32 | Voltage mode: 0=1.5K low-voltage sampling, 1=1K high-voltage |
| BIT6 | 64 | PWM frequency: 0=24kHz, 1=16kHz |
| BIT7 | 128 | Position feedback phase: 0=normal, 1=reverse |

### Status Byte (Address 65/0x41)

| Bit | Weight | Description |
|-----|--------|-------------|
| BIT0 | 1 | Voltage error |
| BIT1 | 2 | Encoder error |
| BIT2 | 4 | Temperature error |
| BIT3 | 8 | Current error |
| BIT4 | 16 | Reserved |
| BIT5 | 32 | Overload error |
| BIT6 | 64 | Reserved |
| BIT7 | 128 | Reserved |

### Unload/LED Alarm Conditions (Addresses 19 & 20)

| Bit | Weight | Description |
|-----|--------|-------------|
| BIT0 | 1 | Voltage protection/alarm |
| BIT1 | 2 | Encoder protection/alarm |
| BIT2 | 4 | Temperature protection/alarm |
| BIT3 | 8 | Current protection/alarm |
| BIT4 | 16 | Reserved |
| BIT5 | 32 | Overload protection/alarm |
| BIT6 | 64 | Reserved |
| BIT7 | 128 | Reserved |

## Operating Modes (Address 33/0x21)

- **Mode 0**: Position servo mode
- **Mode 1**: Constant speed mode
- **Mode 2**: PWM open-loop speed mode
- **Mode 3**: Step mode

## Notes for AI Agents

1. **Calibration**: Writing `128` to `Torque Enable` (addr 40) calibrates current position to `2048`.
2. **Goal Time**: STS servos use Goal Time for movement duration, unlike HLS.
3. **Speed Control**: STS servos have simpler speed control than HLS.
4. **Current Feedback**: STS has less advanced current feedback compared to HLS.
5. **Memory Types**: EEPROM values persist after power off, RAM values reset.