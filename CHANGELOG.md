# Changelog

All notable changes to the vassar-feetech-servo-sdk project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2025-08-06

### Added
- Improved automatic servo disabling - now integrated into `disconnect()` method
- Better KeyboardInterrupt (Ctrl+C) handling to ensure servos are disabled on interrupt

### Changed
- `disconnect()` now automatically calls `disable_all_servos()` before closing port
- Updated torque values in examples to safer levels (80/-120 instead of 500/-300)
- Variable torque example now maxes at 200 instead of 1000

### Fixed
- Servos are now properly disabled when script is interrupted with Ctrl+C

### Removed
- `servo_types.py` example (redundant with other examples)

## [0.3.1] - 2025-08-06

### Added
- `set_operating_mode()` method to configure servo behavior (position/speed/torque/PWM)
- `write_torque()` method for HLS servo torque control with automatic mode switching
- `disable_all_servos()` method and automatic cleanup on controller destruction
- Example script `torque_control.py` demonstrating HLS torque control usage
- Documentation for torque control features in README

### Changed
- Controller now automatically disables all servos when destroyed or exiting context manager for safety

## [0.3.0] - 2025-08-06

### Added
- `set_motor_id()` method to permanently change servo IDs
- Example script `change_servo_id.py` demonstrating ID changes
- Support for both STS and HLS servos in ID changing
- Safety checks and user confirmation for ID changes
- Documentation for changing servo IDs in README

### Changed
- Fixed ping command handling in `set_motor_id()` method

### Removed
- `basic_usage.py` example (functionality covered by other examples)
- Command line interface (CLI) - package is now Python API only

## [0.2.3] - 2025-08-06

### Changed
- Updated package description from "Vassar College's" to "Vassar Robotics'"

## [0.2.2] - 2025-08-06

### Changed
- Cleaned up package structure by removing `__main__.py` (not needed)
- Removed redundant `reader.py` file left over from refactoring

## [0.2.1] - 2025-08-06

### Fixed
- Fixed `set_middle_position()` for HLS servos - now uses `reOfsCal` method instead of torque=128
- HLS servos now properly calibrate to position 2048 using the offset calibration method

## [0.2.0] - 2025-08-06

### Changed
- **BREAKING**: Renamed `ServoReader` to `ServoController` to better reflect comprehensive functionality
- **BREAKING**: Changed constructor to require `servo_ids` as first parameter
- **BREAKING**: Servo type now uses 'sts' instead of 'sms_sts' for STS servos
- **BREAKING**: Removed support for SMS servos (only STS and HLS are supported)
- Improved API design with servo configuration at initialization

### Added
- `set_middle_position()` method to calibrate servos to position 2048
- `read_all_positions()` convenience method to read all configured servos
- `--set-middle` command line option to calibrate servos
- Motor IDs are now optional in read methods (defaults to configured servo_ids)

### Removed
- Support for SMS servos (use STS instead)
- Support for SCSCL servos

## [0.1.0] - 2025-08-06

### Added
- Initial release
- Basic position reading functionality
- Support for STS, SMS, and HLS servos
- Command-line interface
- Auto-detection of serial ports
- Context manager support
- Continuous reading mode