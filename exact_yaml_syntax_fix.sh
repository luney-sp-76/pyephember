#!/bin/bash
# Exact YAML Syntax Fixes Based on Error Analysis

cd /root/config

echo "=== FIXING EXACT YAML SYNTAX ERRORS ==="

# Create backups
cp packages/heating_analytics_package.yaml packages/heating_analytics_package.yaml.syntax_backup
cp packages/luften_eph.yaml packages/luften_eph.yaml.syntax_backup

echo "1. Fixing heating_analytics_package.yaml line 19 - missing closing quote"
# Current: name: "Heating Analytics - Zone ONE Heating Start Time
# Fix: Add missing closing quote
sed -i '19s/name: "Heating Analytics - Zone ONE Heating Start Time$/name: "Heating Analytics - Zone ONE Heating Start Time"/' packages/heating_analytics_package.yaml

echo "2. Fixing luften_eph.yaml line 46 - problematic parentheses in name"
# Current: name: "Luften Dew Point Sensitivity" (°C diff trigger)
# Fix: Remove the problematic part or properly escape it
sed -i '46s/.*/    name: "Luften Dew Point Sensitivity"/' packages/luften_eph.yaml

echo "3. Additional safety fixes..."

# Fix any other potential quote issues
sed -i 's/name: "[^"]*$/&"/' packages/heating_analytics_package.yaml
sed -i 's/name: "[^"]*$/&"/' packages/luften_eph.yaml

# Fix any stray characters that might cause "mapping values not allowed"
sed -i 's/[[:space:]]*$//' packages/heating_analytics_package.yaml
sed -i 's/[[:space:]]*$//' packages/luften_eph.yaml

echo "=== TESTING FIXES ==="

echo "Testing heating_analytics_package.yaml:"
python3 -c "
import yaml
try:
    with open('packages/heating_analytics_package.yaml', 'r') as f:
        yaml.safe_load(f)
    print('✓ heating_analytics_package.yaml - FIXED')
except Exception as e:
    print('✗ heating_analytics_package.yaml - Error:', str(e)[:100])
"

echo "Testing luften_eph.yaml:"
python3 -c "
import yaml
try:
    with open('packages/luften_eph.yaml', 'r') as f:
        yaml.safe_load(f)
    print('✓ luften_eph.yaml - FIXED')
except Exception as e:
    print('✗ luften_eph.yaml - Error:', str(e)[:100])
"

echo "=== TESTING ALL PACKAGES ==="
for file in packages/*.yaml; do
    echo -n "$(basename "$file"): "
    python3 -c "import yaml; yaml.safe_load(open('$file')); print('✓ OK')" 2>/dev/null || echo "✗ ERROR"
done

echo ""
echo "=== IF ALL SHOW ✓ OK, PROCEED WITH ==="
echo "ha core check"
echo "ha core restart"

echo ""
echo "=== IF STILL ERRORS ==="
echo "Check these exact lines manually:"
echo "heating_analytics_package.yaml line 19:"
sed -n '19p' packages/heating_analytics_package.yaml
echo "luften_eph.yaml line 46:"
sed -n '46p' packages/luften_eph.yaml