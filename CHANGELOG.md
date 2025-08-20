# Changelog

All notable changes to the vassar-feetech-servo-sdk project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-01-07

### Added
- New `return_all` parameter to `find_servo_port()` function for getting all available ports
- New `list_ports.py` example script showing port detection usage

### Changed
- **BREAKING**: Default speed parameter in `write_position()` changed from 100 to 0 (maximum speed)
  - Speed parameter: 0 = maximum speed, higher values = slower movement
- `find_servo_port()` can now optionally return all available ports when `return_all=True`
- Teleoperation script now uses the centralized port detection from the SDK
- Teleoperation script restructured with proper `main()` function pattern

### Improved
- Better error handling in teleoperation script when insufficient ports are found
- Port detection code is now shared across the SDK instead of duplicated

## [1.3.0] - 2025-01-07

### Added
- New `read_voltage()` method to read voltage from a single servo
- New `read_voltages()` method to read voltages from multiple servos using group sync read
- Voltage reading example script `read_voltage.py`
- Teleoperation example script `teleoperation.py` with voltage-based leader/follower detection
- Documentation for voltage reading features in README

### Changed
- Teleoperation script now uses voltage-based auto-detection (leader < 9V, follower > 9V)

## [1.2.0] - 2025-08-06

### Added
- New `write_position()` method for efficient position control
  - Uses `SyncWritePosEx` for optimal performance with multiple servos
  - Support for optional torque limit (HLS servos only)
  - Speed and acceleration parameters for motion control
  - Automatically switches servos to position mode when needed
- New example: `position_control.py` demonstrating position control features

### Changed
- `write_torque()` now uses proper torque scaling (0-2047) with 0.95 safety factor
- Default speed parameter in `write_position()` was 100
- Speed parameter range documentation corrected

### Fixed
- Speed parameter range documentation corrected to 0-100 units

## [1.1.0] - 2025-08-06

### Fixed
- Fixed HLS servo torque control to use proper bit format
  - Bit 15 now correctly used for direction (0=forward, 1=reverse)
  - Magnitude calculated based on current units (6.5mA per unit, max 3A)
  - Previous implementation incorrectly used signed integer format

## [0.5.0] - 2025-08-06

### Changed
- **BREAKING**: `write_torque()` now accepts normalized torque values from -1.0 to 1.0 instead of raw values -2047 to 2047
  - -1.0 = full reverse torque
  - 0.0 = no torque  
  - 1.0 = full forward torque
  - The method internally maps these to the hardware range (-2047 to 2047)
- Updated all examples and documentation to use the new normalized torque range

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