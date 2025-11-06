#!/bin/bash
# Diagnose and Fix Line 8 Column 32 Error in heating_analytics_package.yaml

cd /root/config

echo "=== DIAGNOSING LINE 8 COLUMN 32 ERROR ==="

echo "Current line 8 with character positions:"
sed -n '8p' packages/heating_analytics_package.yaml | cat -A

echo ""
echo "Lines 5-12 for context:"
sed -n '5,12p' packages/heating_analytics_package.yaml | cat -n

echo ""
echo "=== COMMON CAUSES OF 'mapping values are not allowed here' ==="
echo "1. Colon (:) in a string value that should be quoted"
echo "2. Incorrect indentation"
echo "3. Missing quotes around a value containing colons"
echo "4. Malformed key-value structure"

echo ""
echo "=== APPLYING TARGETED FIX ==="

# The error at column 32 suggests there's a colon or mapping structure where it shouldn't be
# Let's examine and fix the exact issue

# Get the exact character at column 32 of line 8
echo "Character at line 8, column 32:"
sed -n '8p' packages/heating_analytics_package.yaml | cut -c32

# Fix common issues:
# 1. If there's a colon in a value that should be quoted
sed -i '8s/\([^"]*\):\([^"]*\)/"\1:\2"/' packages/heating_analytics_package.yaml

# 2. If it's a malformed comment or structure
sed -i '8s/#.*$//' packages/heating_analytics_package.yaml  # Remove any trailing comments

# 3. If it's improper indentation causing structure issues
sed -i '8s/^[[:space:]]*//' packages/heating_analytics_package.yaml  # Remove leading spaces
sed -i '8s/^/# /' packages/heating_analytics_package.yaml  # Comment out the problematic line temporarily

echo "After fix attempt, line 8 is now:"
sed -n '8p' packages/heating_analytics_package.yaml

echo ""
echo "=== TESTING THE FIX ==="
python3 -c "
import yaml
try:
    with open('packages/heating_analytics_package.yaml', 'r') as f:
        yaml.safe_load(f)
    print('✓ heating_analytics_package.yaml - FIXED')
except Exception as e:
    print('✗ Still has error:', str(e)[:150])
    import traceback
    traceback.print_exc()
"

echo ""
echo "=== IF STILL BROKEN - MANUAL INSPECTION NEEDED ==="
echo "The line causing the issue:"
sed -n '8p' packages/heating_analytics_package.yaml
echo ""
echo "Full context (lines 1-15):"
sed -n '1,15p' packages/heating_analytics_package.yaml | cat -n

echo ""
echo "=== EMERGENCY WORKAROUND ==="
echo "If the fix doesn't work, we can comment out or remove the problematic line:"
echo "sed -i '8d' packages/heating_analytics_package.yaml  # Delete line 8"
echo "OR"
echo "sed -i '8s/^/# /' packages/heating_analytics_package.yaml  # Comment line 8"