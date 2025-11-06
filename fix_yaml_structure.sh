#!/bin/bash
# Fix Malformed YAML Structure in heating_analytics_package.yaml

cd /root/config

echo "=== FIXING MALFORMED YAML STRUCTURE ==="

# Create backup
cp packages/heating_analytics_package.yaml packages/heating_analytics_package.yaml.structure_backup

echo "Current problematic structure (lines 1-15):"
sed -n '1,15p' packages/heating_analytics_package.yaml | cat -n

echo ""
echo "=== PROBLEM IDENTIFIED ==="
echo "Line 7: 'counter: null' should be 'counter:'"
echo "Lines 8-12: Not properly indented under counter section"
echo "The entity definition needs proper indentation"

echo ""
echo "=== APPLYING STRUCTURAL FIX ==="

# Fix the malformed structure
# 1. Fix line 7 - remove 'null' from counter:
sed -i '7s/counter: null/counter:/' packages/heating_analytics_package.yaml

# 2. Uncomment and fix line 8 - this should be the entity ID under counter
sed -i '8s/^# "\(.*\)"/  zone_one_heating_cycles_today:/' packages/heating_analytics_package.yaml

# 3. Fix indentation for the properties (lines 9-12)
sed -i '9,12s/^      /    /' packages/heating_analytics_package.yaml

echo "After fix, the counter section (lines 5-15):"
sed -n '5,15p' packages/heating_analytics_package.yaml | cat -n

echo ""
echo "=== TESTING THE STRUCTURAL FIX ==="
python3 -c "
import yaml
try:
    with open('packages/heating_analytics_package.yaml', 'r') as f:
        yaml.safe_load(f)
    print('✓ heating_analytics_package.yaml - STRUCTURE FIXED')
except Exception as e:
    print('✗ Still has error:', str(e)[:200])
    import traceback
    traceback.print_exc()
"

echo ""
echo "=== EXPECTED CORRECT STRUCTURE ==="
echo "The counter section should look like:"
echo "counter:"
echo "  zone_one_heating_cycles_today:"
echo "    name: \"Heating Analytics - Zone ONE Heating Cycles Today\""
echo "    icon: mdi:counter"
echo "    initial: 0"
echo "    step: 1"

echo ""
echo "=== IF STILL BROKEN - REBUILD SECTION ==="
echo "We can replace the entire counter section with a working version"