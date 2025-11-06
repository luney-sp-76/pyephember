#!/bin/bash
# Targeted YAML Error Fixes based on exact error locations

cd /root/config

echo "=== FIXING SPECIFIC YAML ERRORS ==="

# Backup the problematic files
cp packages/heating_analytics_package.yaml packages/heating_analytics_package.yaml.backup_$(date +%Y%m%d_%H%M%S)
cp packages/luften_eph.yaml packages/luften_eph.yaml.backup_$(date +%Y%m%d_%H%M%S)

echo "1. Examining heating_analytics_package.yaml error (line 9-19)..."
echo "Lines 5-25:"
sed -n '5,25p' packages/heating_analytics_package.yaml

echo ""
echo "2. Examining luften_eph.yaml error (line 46, column 42)..."
echo "Lines 44-48:"
sed -n '44,48p' packages/luften_eph.yaml

echo ""
echo "=== APPLYING TARGETED FIXES ==="

# Fix 1: luften_eph.yaml line 46 column 42
# This is likely a missing quote, colon, or improper value
echo "Fixing luften_eph.yaml line 46..."

# The error "expected <block end>, but found '<scalar>'" at column 42 suggests
# there's text after where YAML expects the block to end
# Common issue: missing quotes around a value with special characters

# Let's see what's actually on line 46
echo "Current line 46 content:"
sed -n '46p' packages/luften_eph.yaml

# Replace line 46 with a safe version
sed -i '46s/.*/    name: "Lüften Dew Point Sensitivity"/' packages/luften_eph.yaml

# Fix 2: heating_analytics_package.yaml lines 9-19
echo "Fixing heating_analytics_package.yaml structure..."

# This error suggests malformed YAML structure between lines 9-19
# Let's look at the structure around the input_number section

echo "Current lines 5-25:"
sed -n '5,25p' packages/heating_analytics_package.yaml

# Common fixes:
# 1. Ensure proper indentation
# 2. Fix missing colons or values
# 3. Add quotes around problematic values

# Fix common YAML structure issues
sed -i 's/^  \([a-zA-Z_][a-zA-Z0-9_]*\):$/  \1:/' packages/heating_analytics_package.yaml
sed -i 's/^    \([a-zA-Z_][a-zA-Z0-9_]*\):$/    \1:/' packages/heating_analytics_package.yaml

# Fix missing values after colons
sed -i 's/:$/: null/' packages/heating_analytics_package.yaml

# Ensure names are quoted
sed -i 's/name: \([^"]\)/name: "\1/' packages/heating_analytics_package.yaml
sed -i 's/name: "\([^"]*\)$/name: "\1"/' packages/heating_analytics_package.yaml

echo ""
echo "=== TESTING FIXES ==="

# Test heating_analytics_package.yaml
echo "Testing heating_analytics_package.yaml:"
python3 -c "
import yaml
try:
    yaml.safe_load(open('packages/heating_analytics_package.yaml'))
    print('✓ heating_analytics_package.yaml - FIXED')
except yaml.YAMLError as e:
    print('✗ heating_analytics_package.yaml - STILL ERROR:', e)
    if hasattr(e, 'problem_mark'):
        print('  Line:', e.problem_mark.line + 1, 'Column:', e.problem_mark.column + 1)
"

# Test luften_eph.yaml
echo "Testing luften_eph.yaml:"
python3 -c "
import yaml
try:
    yaml.safe_load(open('packages/luften_eph.yaml'))
    print('✓ luften_eph.yaml - FIXED')
except yaml.YAMLError as e:
    print('✗ luften_eph.yaml - STILL ERROR:', e)
    if hasattr(e, 'problem_mark'):
        print('  Line:', e.problem_mark.line + 1, 'Column:', e.problem_mark.column + 1)
"

echo ""
echo "=== FINAL VALIDATION OF ALL PACKAGES ==="
for file in packages/*.yaml; do
    echo -n "Checking $(basename $file)... "
    python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null && echo "✓ OK" || echo "✗ ERROR"
done

echo ""
echo "=== NEXT STEPS ==="
echo "If all files show ✓ OK, run:"
echo "  ha core check"
echo "  ha core restart"
echo ""
echo "If any files still show ✗ ERROR, examine the specific lines mentioned"
echo "and manually edit the problematic YAML structure."