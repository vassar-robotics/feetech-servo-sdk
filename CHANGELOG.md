# Changelog

All notable changes to the vassar-feetech-servo-sdk project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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