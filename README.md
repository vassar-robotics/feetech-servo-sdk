# Feetech Servo SDK

Minimal Python SDK for Feetech servo motors - clean, simple, and effective.


This minimal implementation is built using the official Feetech SDK from: https://gitee.com/ftservo/FTServo_Python

## Requirements

- Python 3.x
- pyserial: `pip install pyserial`
- pyzmq: `pip install pyzmq` (for basic_send_commands.py)
- scservo_sdk (included in the `scservo_sdk/` directory)

## Scripts

### read_leader_positions.py
Continuously reads and displays joint positions from the robot at 30 Hz.

```bash
# Auto-detect robot port and display positions
python read_leader_positions.py

# Specify port manually
python read_leader_positions.py --port=/dev/ttyUSB0

# Custom motor IDs and frequency
python read_leader_positions.py --motor_ids=1,2,3,4 --hz=60
```

### set_middle_position.py
Sets the current position of each servo to read as 2048 (middle position). Uses the special torque=128 command - the calibration takes effect immediately.

```bash
# Calibrate all servos to middle position
python set_middle_position.py

# Custom motor IDs
python set_middle_position.py --motor_ids=1,2,3,4,5,6,7,8

# Specify port manually
python set_middle_position.py --port=/dev/ttyUSB0
```

### basic_send_commands.py
Reads joint positions from the SO101 robot and sends them via ZMQ to a remote endpoint. Displays positions in the terminal while broadcasting.

```bash
# Read positions and send to tcp://10.1.10.85:5000
python basic_send_commands.py

# Specify custom motor IDs
python basic_send_commands.py --motor_ids=1,2,3,4,5,6

# Custom frequency (default: 10 Hz)
python basic_send_commands.py --hz=30

# Specify port manually
python basic_send_commands.py --port=COM3
```
