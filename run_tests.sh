#!/bin/bash
# Run tests for vassar-feetech-servo-sdk

echo "Running vassar-feetech-servo-sdk test suite..."
echo "=============================================="

# Install development dependencies
echo "Installing development dependencies..."
pip install -r requirements-dev.txt

echo ""
echo "Running tests with coverage..."
echo "------------------------------"

# Run tests with coverage
python -m pytest tests/ -v --cov=vassar_feetech_servo_sdk --cov-report=term-missing

# Run specific test groups if needed
# python -m pytest tests/test_controller.py -v  # Just controller tests
# python -m pytest tests/test_cli.py -v         # Just CLI tests