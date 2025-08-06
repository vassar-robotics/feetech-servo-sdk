# SCS Communication Protocol

This document outlines the FT-SCS custom communication protocol used by Feetech servos.

## 1. Protocol Overview

- **Physical Layer**: Communication is handled via TTL level (for STS) or RS485 (for SMS) asynchronous serial.
- **Communication Mode**: Asynchronous half-duplex, with separate asynchronous processing for sending and receiving.
- **Interaction Model**: The controller sends an **Instruction Frame**, and the servo replies with a **Response Frame**.
- **Addressing**: Each servo on the bus must have a unique ID (0-253). The controller specifies the ID in the instruction frame.
- **Broadcast ID**: ID `254` (0xFE) is the broadcast ID. All servos will execute the command, but none will send a response frame (except for PING, which should not be used with broadcast).
- **Serial Format**: 1 start bit, 8 data bits, 1 stop bit, no parity (10 bits total).
- **Endianness**:
  - **Magnetic Encoder Servos (STS/HLS)**: Little-endian (low byte first).
  - **Potentiometer Servos**: Big-endian (high byte first).

---

## 2. Instruction Frame

The format for a command sent from the controller to the servo.

| Header | ID | Length | Instruction | Parameters | Checksum |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `0xFF 0xFF` | Servo ID | Data Length | Command | `Param 1`...`Param N` | `Checksum` |

- **Header**: Two consecutive `0xFF` bytes mark the start of a packet.
- **ID**: The unique ID of the target servo (0-253), or the broadcast ID (254).
- **Length**: The number of bytes following this field, calculated as `N + 2` (where N is the number of parameters).
- **Instruction**: The command code to be executed (see section 4).
- **Parameters**: Control information required by the instruction.
- **Checksum**: A value used to verify data integrity.
  - **Formula**: `Checksum = ~ (ID + Length + Instruction + Param 1 + ... + Param N)`
  - `~` denotes a bitwise NOT (inversion).
  - If the sum exceeds 255, only the lowest byte is used for the calculation.

---

## 3. Response Frame

The format for a response sent from the servo back to the controller.

| Header | ID | Length | Status | Parameters | Checksum |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `0xFF 0xFF` | Servo ID | Data Length | Error Code | `Param 1`...`Param N` | `Checksum` |

- **Status (Error Code)**: A byte indicating the current status of the servo. A value of `0` means no error. For non-zero values, each bit corresponds to a specific error type (see the `Status Byte` section in the servo's memory table).

---

## 4. Instruction Types

| Instruction | Value | Description |
|---|---|---|
| `PING` | `0x01` | Checks the servo's operational status. |
| `READ DATA` | `0x02` | Reads data from the servo's memory table. |
| `WRITE DATA` | `0x03` | Writes data to the servo's memory table. |
| `REG WRITE` | `0x04` | Asynchronous write. Data is stored in a buffer and executed later. |
| `ACTION` | `0x05` | Triggers the execution of a pending `REG WRITE` command. |
| `SYNC WRITE` | `0x83` | Synchronously writes data to multiple servos in a single command. |
| `SYNC READ` | `0x82` | Synchronously reads data from multiple servos. |
| `RESET` | `0x0A` | Resets the servo's status (e.g., resets multi-turn count). |
| `POSITION CALIBRATE` | `0x0B` | Recalibrates the current position to a specified value. |
| `RESTORE PARAMS` | `0x06` | Restores servo parameters to their factory defaults (excluding ID). |
| `BACKUP PARAMS` | `0x09` | Backs up the current parameters for later restoration. |
| `REBOOT` | `0x08` | Reboots the servo. |

### 4.1 PING

- **Function**: Queries the operational status of a servo.
- **Instruction**: `0x01`
- **Parameters**: None
- **Example**: Ping servo with ID `1`.
  - **Instruction Frame**: `FF FF 01 02 01 FB`
  - **Response Frame**: `FF FF 01 02 00 FC` (Status `00` means no error).

### 4.2 READ DATA

- **Function**: Reads a block of data from the servo's memory table.
- **Instruction**: `0x02`
- **Parameters**:
  - `Param 1`: Starting memory address.
  - `Param 2`: Length of data to read (in bytes).
- **Example**: Read 2 bytes from address `0x38` (Present Position) on servo ID `1`.
  - **Instruction Frame**: `FF FF 01 04 02 38 02 BE`
  - **Response Frame**: `FF FF 01 04 00 18 05 DD`
  - **Result**: The parameters `18 05` represent the position. For little-endian servos, this is `0x0518`, which is `1304` in decimal.

### 4.3 WRITE DATA

- **Function**: Writes a block of data to the servo's memory table.
- **Instruction**: `0x03`
- **Parameters**:
  - `Param 1`: Starting memory address.
  - `Param 2...N`: Data bytes to write.
- **Example**: Set the Goal Position of servo ID `1` to `2048` (`0x0800`) at a speed of `1000` (`0x03E8`). The target address is `0x2A`.
  - **Instruction Frame**: `FF FF 01 09 03 2A 00 08 00 00 E8 03 D5`
    - Address: `2A`
    - Position: `00 08` (2048)
    - Time: `00 00` (reserved/0)
    - Speed: `E8 03` (1000)
  - **Response Frame**: `FF FF 01 02 00 FC`

### 4.4 REG WRITE (Asynchronous Write)

- **Function**: Same as `WRITE DATA`, but the action is buffered and not executed immediately.
- **Instruction**: `0x04`
- **Behavior**: Upon receiving, the servo stores the data in a buffer and sets an internal "pending write" flag. The action is only performed when an `ACTION` command is received.

### 4.5 ACTION

- **Function**: Triggers the execution of all pending `REG WRITE` commands on one or more servos.
- **Instruction**: `0x05`
- **Parameters**: None
- **Behavior**: This is useful for synchronizing the movement of multiple servos. Typically, you send a `REG WRITE` to each servo individually, then send a single broadcast `ACTION` command to make them all move simultaneously.
- **Example**: Trigger pending writes on all servos.
  - **Instruction Frame**: `FF FF FE 02 05 FA` (Note the broadcast ID `FE`)
  - **Response Frame**: None (since it's a broadcast command).

### 4.6 SYNC WRITE

- **Function**: A more efficient way to control multiple servos simultaneously in a single command.
- **Instruction**: `0x83`
- **ID**: Must be broadcast ID `0xFE`.
- **Length**: `(L + 1) * N + 4`, where `L` is data length per servo, and `N` is the number of servos.
- **Parameters**:
  - `Param 1`: Starting memory address (must be the same for all servos).
  - `Param 2`: Length of data for each servo (`L`).
  - `Param 3...`: A repeating block for each servo: `[ID, Data 1, Data 2, ... Data L]`
- **Example**: Set 4 servos (IDs 1-4) to position `2048` and speed `1000`. Address is `0x2A`, data length per servo is 6.
  - **Instruction Frame**: `FF FF FE 20 83 2A 06 01 00 08 00 00 E8 03 02 00 08 00 00 E8 03 03 00 08 00 00 E8 03 04 00 08 00 00 E8 03 58`

### 4.7 SYNC READ

- **Function**: Simultaneously queries the same memory address range from multiple servos.
- **Instruction**: `0x82`
- **ID**: Must be broadcast ID `0xFE`.
- **Length**: `N + 4`, where `N` is the number of servos.
- **Parameters**:
  - `Param 1`: Starting memory address.
  - `Param 2`: Length of data to read.
  - `Param 3...N+2`: The IDs of the servos to query.
- **Behavior**: Each servo will respond in the order its ID appeared in the instruction frame.

### 4.8 RESET

- **Function**: Resets the servo's status, including the multi-turn position counter.
- **Instruction**: `0x0A`
- **Example**: Reset servo ID `1`.
  - **Instruction Frame**: `FF FF 01 02 0A F2`

### 4.9 POSITION CALIBRATE

- **Function**: Recalibrates the current physical position to a new value.
- **Instruction**: `0x0B`
- **Parameters**:
  - **None**: Calibrates the current position to the middle point (`2048`).
  - **2 bytes**: Calibrates the current position to the specified value.
- **Support**:
  - **SMS**: Not supported. Use `Torque Enable = 128` instead.
  - **STS (>=3.10)**: Supported with and without parameters.
  - **HLS (<=3.42)**: Supported without parameters only.
  - **HLS (>=3.43)**: Supported with and without parameters.

### 4.10 RESTORE PARAMS

- **Function**: Restores all parameters in the EEPROM area to their factory default values, except for the servo ID.
- **Instruction**: `0x06`

### 4.11 BACKUP PARAMS

- **Function**: Creates a backup of the current EEPROM parameters, which can be restored using the `RESTORE PARAMS` command.
- **Instruction**: `0x09`

### 4.12 REBOOT

- **Function**: Reboots the servo.
- **Instruction**: `0x08`
- **Response**: None. The servo will take ~800ms to restart.