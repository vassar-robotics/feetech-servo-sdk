# HLS Series Servo Memory Table

HLS servos use magnetic encoding and the FT-SCS custom protocol. Default serial configuration: 1Mbps baud rate, 8 data bits, no parity, 1 stop bit.

## Version Information (Read-only)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 0 (0x00) | Firmware Major Version | R | 1 | 3 | - | Main firmware version |
| 1 (0x01) | Firmware Minor Version | R | 1 | - | 40-59 | Sub firmware version |
| 2 (0x02) | Endianness | R | 1 | 0 | - | 0=little-endian storage |
| 3 (0x03) | Servo Major Version | R | 1 | 10 | - | Main servo version |
| 4 (0x04) | Servo Minor Version | R | 1 | - | - | Sub servo version |

## EEPROM Configuration (Non-volatile)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 5 (0x05) | Primary ID | RW | 1 | 1 | 0-253 | Unique primary ID on bus |
| 6 (0x06) | Baud Rate | RW | 1 | 0 | 0-7 | 0=1M, 1=500K, 2=250K, 3=128K, 4=115.2K, 5=76.8K, 6=57.6K, 7=38.4K |
| 7 (0x07) | Secondary ID | RW | 1 | 0 | 0-253 | Secondary ID (write commands only) |
| 8 (0x08) | Response Level | RW | 1 | 1 | 0-1 | 0=read/ping only, 1=all commands |
| 9 (0x09) | Min Angle Limit | RW | 2 | 0 | 0-4094 | Min position (0.087°/unit). 0 for multi-turn |
| 11 (0x0B) | Max Angle Limit | RW | 2 | 4095 | 1-4095 | Max position (0.087°/unit). 0 for multi-turn |
| 13 (0x0D) | Max Temperature | RW | 1 | 70 | 0-100 | Maximum temperature limit (°C) |
| 14 (0x0E) | Max Voltage | RW | 1 | - | 0-254 | Maximum voltage (0.1V/unit) |
| 15 (0x0F) | Min Voltage | RW | 1 | 40 | 0-254 | Minimum voltage (0.1V/unit) |
| 16 (0x10) | Max Torque | RW | 2 | 980 | 0-1000 | Max torque (0.1%). Loaded to addr 48 on startup |
| 18 (0x12) | Phase | RW | 1 | - | 0-254 | Special function byte - do not modify |
| 19 (0x13) | Unload Conditions | RW | 1 | - | 0-254 | Protection enable bits (1=enable, 0=disable) |
| 20 (0x14) | LED Alarm Conditions | RW | 1 | - | 0-254 | LED alarm enable bits (1=enable, 0=disable) |
| 21 (0x15) | Position P Gain | RW | 1 | - | 0-254 | Position loop P coefficient. Loaded to addr 50 |
| 22 (0x16) | Position D Gain | RW | 1 | - | 0-254 | Position loop D coefficient. Loaded to addr 51 |
| 23 (0x17) | Position I Gain | RW | 1 | 0 | 0-254 | Position loop I coefficient. Loaded to addr 52 |
| 24 (0x18) | Min Starting Force | RW | 1 | - | 0-254 | Minimum startup torque (0.1%) |
| 25 (0x19) | Integral Limit | RW | 1 | 0 | 0-254 | Max integral = value×4. 0=no limit. Modes 0,4 |
| 26 (0x1A) | CW Dead Zone | RW | 1 | 1 | 0-16 | Clockwise dead zone (0.087°/unit) |
| 27 (0x1B) | CCW Dead Zone | RW | 1 | 1 | 0-16 | Counter-clockwise dead zone (0.087°/unit) |
| 28 (0x1C) | Protection Current | RW | 2 | - | 0-2047 | Current limit (6.5mA/unit). Loaded to addr 44 |
| 30 (0x1E) | Angle Resolution | RW | 1 | 1 | 1-128 | Sensor resolution multiplier |
| 31 (0x1F) | Position Offset | RW | 2 | 0 | -4095 to 4095 | Position offset (0.087°/unit). BIT15=direction |
| 33 (0x21) | Operating Mode | RW | 1 | 0 | 0-3 | 0=Position, 1=Speed, 2=Current, 3=PWM |
| 34 (0x22) | Current P Gain | RW | 1 | - | 0-254 | Current loop P coefficient |
| 35 (0x23) | Current I Gain | RW | 1 | - | 0-254 | Current loop I coefficient |
| 36 (0x24) | Reserved | RW | 1 | - | - | Undefined |
| 37 (0x25) | Speed P Gain | RW | 1 | - | 0-254 | Speed loop P coefficient (Mode 1) |
| 38 (0x26) | Overcurrent Time | RW | 1 | 200 | 0-254 | Overcurrent protection time (10ms/unit) |
| 39 (0x27) | Speed I Gain | RW | 1 | - | 0-254 | Speed loop I coefficient (Mode 1) |

## SRAM Control (Volatile)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 40 (0x28) | Torque Enable | RW | 1 | 0 | 0-2 | 0=off, 1=on, 2=damping mode |
| 41 (0x29) | Acceleration | RW | 1 | 0 | 0-254 | Acceleration (8.7°/s²/unit). 0=max acceleration |
| 42 (0x2A) | Goal Position | RW | 2 | 0 | -32767 to 32767 | Target position (0.087°/unit). BIT15=direction |
| 44 (0x2C) | Goal Torque | RW | 2 | From addr 28 | -2047 to 2047 | Target torque/current (6.5mA/unit). Mode dependent |
| 46 (0x2E) | Goal Speed | RW | 2 | Factory max | -32767 to 32767 | Max speed (0.732RPM/unit). 0=stop. BIT15=direction |
| 48 (0x30) | Torque Limit | RW | 2 | From addr 16 | 0-1000 | Stall torque limit (0.1%) |
| 50 (0x32) | Kp | RW | 1 | From addr 21 | 0-254 | Position loop P coefficient |
| 51 (0x33) | Kd | RW | 1 | From addr 22 | 0-254 | Position loop D coefficient |
| 52 (0x34) | Ki | RW | 1 | From addr 23 | 0-254 | Position loop I coefficient |
| 53 (0x35) | Km | RW | 1 | 0 | 0-1 | 0=dual loop, 1=position only. Removed in fw>=2.42 |
| 54 (0x36) | Reserved | RW | 1 | - | - | Undefined |
| 55 (0x37) | Lock Flag | RW | 1 | 1 | 0-1 | 0=save EEPROM changes, 1=don't save |

## SRAM Feedback (Read-only)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 56 (0x38) | Present Position | R | 2 | - | - | Current position (0.087°/unit). BIT15=direction |
| 58 (0x3A) | Present Speed | R | 2 | - | - | Current speed (0.732RPM/unit). BIT15=direction |
| 60 (0x3C) | Present Load | R | 2 | - | - | Current PWM duty (0.1%). BIT10=direction |
| 62 (0x3E) | Present Voltage | R | 1 | - | - | Current voltage (0.1V/unit) |
| 63 (0x3F) | Present Temperature | R | 1 | - | - | Current temperature (°C) |
| 64 (0x40) | Async Write Flag | R | 1 | 0 | - | Flag for async write operations |
| 65 (0x41) | Status | R | 1 | 0 | - | Error flags (see Status Bits section) |
| 66 (0x42) | Moving Flag | R | 1 | 0 | - | BIT0=moving(1)/stopped(0), BIT1=reached(0)/not(1) |
| 67 (0x43) | Target Position | R | 2 | - | - | Current target position (0.087°/unit) |
| 69 (0x45) | Present Current | R | 2 | - | - | Motor phase current (6.5mA/unit) |
| 71 (0x47) | Reserved | R | 2 | - | - | Undefined |
| 73 (0x49) | Current Offset | R | 2 | - | - | Current zero-point offset |

## Factory Parameters (Read-only)

| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 77 (0x4D) | vFk(*10) | R | 1 | - | - | Factory parameter |
| 78 (0x4E) | vKgI | R | 1 | - | - | Factory parameter |
| 79 (0x4F) | pFk(*10) | R | 1 | - | - | Factory parameter |
| 80 (0x50) | Speed Threshold | R | 1 | - | - | Movement speed threshold |
| 81 (0x51) | DTs(ms) | R | 1 | - | - | Factory parameter |
| 82 (0x52) | eFk(*10) | R | 1 | - | - | Factory parameter |
| 83 (0x53) | Vk(ms) | R | 1 | - | - | Factory parameter |
| 84 (0x54) | Max Speed Limit | R | 1 | - | - | Maximum speed limit |
| 85 (0x55) | Acceleration Limit | R | 1 | - | - | Acceleration limit |
| 86 (0x56) | Acceleration Multiplier | R | 1 | - | - | Acceleration multiplier |

## Special Byte Explanations

### Phase Byte (Address 18/0x12)

| Bit | Weight | Description |
|-----|--------|-------------|
| BIT0 | 1 | Current drive phase: 0=normal, 1=reverse (invalid in fw>=3.42) |
| BIT1 | 2 | Current feedback phase: 0=normal, 1=reverse |
| BIT2 | 4 | Drive bridge phase: 0=normal, 1=reverse |
| BIT3 | 8 | Speed feedback phase: 0=normal, 1=reverse |
| BIT4 | 16 | Angle feedback mode: 0=single turn, 1=multi-turn |
| BIT5 | 32 | Bridge type: 0=discrete H-bridge, 1=integrated H-bridge |
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

### Unload Conditions (Address 19/0x13)

| Bit | Weight | Description |
|-----|--------|-------------|
| BIT0 | 1 | Voltage protection |
| BIT1 | 2 | Encoder protection |
| BIT2 | 4 | Temperature protection |
| BIT3 | 8 | Current protection |
| BIT4 | 16 | Reserved |
| BIT5 | 32 | Overload protection |
| BIT6 | 64 | Reserved |
| BIT7 | 128 | Reserved |

### LED Alarm Conditions (Address 20/0x14)

| Bit | Weight | Description |
|-----|--------|-------------|
| BIT0 | 1 | Voltage alarm |
| BIT1 | 2 | Encoder alarm |
| BIT2 | 4 | Temperature alarm |
| BIT3 | 8 | Current alarm |
| BIT4 | 16 | Reserved |
| BIT5 | 32 | Overload alarm |
| BIT6 | 64 | Reserved |
| BIT7 | 128 | Reserved |

## Operating Modes (Address 33/0x21)

- **Mode 0**: Position servo mode
- **Mode 1**: Constant speed mode
- **Mode 2**: Constant current/torque mode
- **Mode 3**: PWM open-loop speed mode

## Notes for AI Agents

1. **Position Values**: 16-bit signed values, 0.087° per unit
2. **Multi-turn Support**: HLS servos support multi-turn absolute positioning
3. **Current Control**: HLS has advanced current control capabilities
4. **Calibration**: Unlike STS, HLS uses offset calibration method (reOfsCal)
5. **Protection Features**: Comprehensive protection with configurable conditions
6. **PID Control**: Full PID control available for position, speed, and current loops