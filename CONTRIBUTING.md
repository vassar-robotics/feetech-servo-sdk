# Contributing to vassar-feetech-servo-sdk

Thank you for your interest in contributing to the vassar-feetech-servo-sdk project! Since this package is now being used in production, we follow strict guidelines to ensure backwards compatibility.

## 🚨 No Breaking Changes Policy

**This package is used in production environments. We do NOT accept breaking changes.**

### What are Breaking Changes?

Breaking changes include:
- Removing or renaming public functions, methods, or classes
- Changing function/method signatures (parameters, return types)
- Changing default behavior of existing functions
- Removing or renaming command-line options
- Changing the structure of returned data

### How to Add New Features

✅ **DO:**
- Add new optional parameters with default values
- Add new methods/functions alongside existing ones
- Add new command-line options
- Extend functionality while preserving existing behavior
- Deprecate old features before removal (with warnings)

❌ **DON'T:**
- Remove or rename existing functions/methods
- Change required parameters
- Modify return types or data structures
- Change default values that affect behavior

### Examples

**Good - Adding Optional Parameter:**
```python
# Original
def read_positions(self, motor_ids=None):
    ...

# Good addition - optional parameter with default
def read_positions(self, motor_ids=None, timeout=5.0):
    ...
```

**Bad - Changing Required Parameter:**
```python
# Original
def __init__(self, servo_ids, servo_type="sts"):
    ...

# BAD - This breaks existing code!
def __init__(self, config_dict):  # ❌ Breaking change!
    ...
```

**Good - Adding New Method:**
```python
# Add new functionality without changing existing
def set_motor_id(self, current_id, new_id):  # ✅ New method
    ...
```

## Semantic Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Breaking changes (NOT ALLOWED)
- **MINOR** (0.X.0): New features, backwards compatible
- **PATCH** (0.0.X): Bug fixes, backwards compatible

Since we're at v0.3.0, we should aim to reach v1.0.0 when the API is completely stable.

## Development Process

1. **Discuss First**: Open an issue before making significant changes
2. **Test Thoroughly**: Ensure all existing tests pass
3. **Add Tests**: New features must include tests
4. **Update Docs**: Update README and docstrings
5. **Update CHANGELOG**: Document all changes

## Testing for Compatibility

Before submitting a PR:

```bash
# Run all tests
python -m pytest tests/ -v

# Check import compatibility
python -c "from vassar_feetech_servo_sdk import *"

# Test CLI still works
vassar-servo --help
```

## Deprecation Process

If something must be changed:

1. Add deprecation warning in version X.Y.0
2. Keep old functionality working
3. Document migration path
4. Wait at least 2 minor versions
5. Only remove in next major version (if ever)

Example:
```python
import warnings

def old_method(self):
    warnings.warn(
        "old_method is deprecated, use new_method instead",
        DeprecationWarning,
        stacklevel=2
    )
    return self.new_method()
```

## Code Style

- Follow PEP 8
- Use type hints for new code
- Add docstrings for all public methods
- Keep line length under 88 characters (Black formatter)

## Questions?

If you're unsure whether a change would be breaking, please open an issue first!