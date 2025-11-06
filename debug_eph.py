#!/usr/bin/env python3
"""
Debug script to test EPH imports and environment
"""

import sys
import os

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Current working directory:", os.getcwd())
print("Python path:", sys.path)
print()

# Test environment variables
print("Environment variables:")
print("EPH_USERNAME:", os.getenv('EPH_USERNAME', 'NOT_SET'))
print("EPH_PASSWORD:", "SET" if os.getenv('EPH_PASSWORD') else "NOT_SET")
print()

# Test imports
try:
    import pyephember2
    print("✓ pyephember2 import successful")
    print("Module location:", pyephember2.__file__)
except ImportError as e:
    print("✗ pyephember2 import failed:", e)
    sys.exit(1)

try:
    from pyephember2.pyephember2 import EphEmber
    print("✓ EphEmber import successful")
except ImportError as e:
    print("✗ EphEmber import failed:", e)
    sys.exit(1)

try:
    # Test basic instantiation with dummy credentials
    helper = EphEmber("test", "test")
    print("✓ EphEmber instantiation successful")
except Exception as e:
    print("✗ EphEmber instantiation failed:", e)

print("\nAll basic tests passed!")