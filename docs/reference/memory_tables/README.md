# Feetech Servo Memory Tables

This directory contains memory maps and register documentation for Feetech servos.

## Files

- `sts_memory_table.md` - Memory map for STS series servos
- `hls_memory_table.md` - Memory map for HLS series servos

## Format Guidelines

Memory tables should be formatted as markdown tables with the following columns:
- **Address** - Memory address (decimal and hex)
- **Name** - Register name
- **Access** - R (read), W (write), or RW (read/write)
- **Size** - Number of bytes
- **Default** - Default value
- **Range** - Valid value range
- **Description** - What the register controls

## Example Format

```markdown
| Address | Name | Access | Size | Default | Range | Description |
|---------|------|--------|------|---------|-------|-------------|
| 0 (0x00) | Model Number L | R | 1 | - | - | Lower byte of model number |
| 1 (0x01) | Model Number H | R | 1 | - | - | Upper byte of model number |
| 40 (0x28) | Torque Enable | RW | 1 | 0 | 0-128 | 0=off, 1=on, 128=calibrate to middle |
| 56 (0x38) | Present Position L | R | 1 | - | 0-255 | Lower byte of current position |
| 57 (0x39) | Present Position H | R | 1 | - | 0-15 | Upper byte of current position |
```

## Usage for AI Agents

These tables provide critical context for:
- Understanding which addresses to read/write
- Knowing valid value ranges
- Understanding register purposes
- Implementing protocol handlers correctly