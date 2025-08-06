# Feetech Servo SDK Examples

This directory contains examples for using the Feetech servo SDK.

## Directory Structure

### official_feetech/
Contains the official examples from the Feetech repository (https://gitee.com/ftservo/FTServo_Python/tree/main)

- **sms_sts/** - Examples for SMS/STS series servos
  - ping.py - Test servo communication
  - read.py - Read servo parameters
  - write.py - Write servo parameters
  - read_write.py - Combined read/write operations
  - sync_read.py - Synchronized reading from multiple servos
  - sync_write.py - Synchronized writing to multiple servos
  - wheel.py - Wheel mode operations
  - reg_write.py - Register write operations

- **scscl/** - Examples for SCSCL series servos
  - Similar examples as sms_sts series

- **hls/** - Examples for HLS series servos
  - Similar examples as sms_sts series
  - Additional: reset.py - Reset servo to factory defaults
  - Additional: ofscal.py - Offset calibration

- **scservo_sdk_official/** - The official SDK library code (for reference)
  - Can be compared with the SDK in the root project directory

- **README_OFFICIAL.md** - The original README from the official repository

## Usage

To run any example:

1. Navigate to the appropriate directory based on your servo series
2. Run the example with Python:
   ```bash
   python3 examples/official_feetech/sms_sts/ping.py
   ```

Make sure to:
- Configure the correct serial port in the example files
- Set the appropriate baud rate for your servo
- Have the required permissions to access the serial port

## Note

The examples use the scservo_sdk library. Your project has its own copy in the root `scservo_sdk/` directory. If you want to use the official version instead, you can either:
1. Replace your scservo_sdk with the one in `official_feetech/scservo_sdk_official/`
2. Or modify the import paths in the example scripts