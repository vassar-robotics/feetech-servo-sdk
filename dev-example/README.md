# Dev Example - Official Feetech SDK Examples

This directory contains the official example code from Feetech for their servo SDK. These examples are included for development reference but are **NOT** part of the `vassar-feetech-servo-sdk` package.

**Source**: These examples are adapted from the official Feetech repository: https://gitee.com/ftservo/FTServo_Python

## Purpose

- Reference implementation examples from Feetech
- Testing and debugging servo operations
- Comparing behavior between raw protocol usage and our SDK
- Development-only - excluded from PyPI package

## Structure

- `hls/` - Examples for HLS series servos (with torque control)
- `sts/` - Examples for STS series servos

## Usage

These examples demonstrate basic servo operations using the Feetech protocol. To run them, you need to either:

1. Install the package first:
```bash
pip install -e .
cd dev-example/sts
python ping.py
```

2. Or run from the project root:
```bash
python dev-example/sts/ping.py
```

## Note

**Important**: These examples import from `scservo_sdk` which is bundled with our main package. They need to be run from the project root or with the package installed.

Our SDK (`vassar-feetech-servo-sdk`) provides a cleaner, more Pythonic API compared to these raw examples. For production use, please use the main SDK API instead of these examples.