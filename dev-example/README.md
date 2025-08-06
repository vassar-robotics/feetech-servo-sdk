# Dev Example - Official Feetech SDK Examples

This directory contains the official example code from Feetech for their servo SDK. These examples are included for development reference but are **NOT** part of the `vassar-feetech-servo-sdk` package.

## Purpose

- Reference implementation from Feetech
- Testing and debugging the wrapped SDK
- Comparing behavior between official examples and our SDK
- Development-only - excluded from PyPI package

## Structure

- `hls/` - Examples for HLS series servos (with torque control)
- `sms_sts/` - Examples for SMS/STS series servos  
- `scscl/` - Examples for SCSCL series servos (not supported in our SDK)
- `scservo_sdk_official/` - The official SDK implementation

## Usage

These examples use the bundled `scservo_sdk_official` directly. To run them:

```bash
cd dev-example/sms_sts
python ping.py
```

## Note

Our SDK (`vassar-feetech-servo-sdk`) provides a cleaner, more Pythonic API compared to these raw examples. For production use, please use the main SDK API instead of these examples.