#!/bin/bash
# Script to build and install the vassar-feetech-servo-sdk package

echo "Building vassar-feetech-servo-sdk package..."

# Clean previous builds
rm -rf build/ dist/ *.egg-info

# Install build tools if needed
pip install --upgrade pip setuptools wheel build

# Build the package
python -m build

echo "Package built successfully!"
echo ""
echo "To install locally for development:"
echo "  pip install -e ."
echo ""
echo "To install the built package:"
echo "  pip install dist/vassar_feetech_servo_sdk-*.whl"
echo ""
echo "To upload to TestPyPI (for testing):"
echo "  pip install twine"
echo "  twine upload --repository testpypi dist/*"
echo ""
echo "To upload to PyPI (for release):"
echo "  twine upload dist/*"