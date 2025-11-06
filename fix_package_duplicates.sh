#!/bin/bash
# Complete Package Fix Script
# This script fixes all duplicate names and YAML syntax errors

cd /root/config

echo "=== FIXING DUPLICATE PACKAGE NAMES AND YAML ERRORS ==="

# 1. Create comprehensive backup
echo "Creating backup..."
cp configuration.yaml configuration.yaml.backup_$(date +%Y%m%d_%H%M%S)
cp -r packages packages.backup_$(date +%Y%m%d_%H%M%S)

# 2. Fix YAML syntax error in luften_eph.yaml first
echo "Fixing YAML syntax error in luften_eph.yaml..."
# This usually happens when there's a missing value or improper indentation
# Let's examine line 46 and surrounding area
echo "Checking line 46 in luften_eph.yaml:"
sed -n '40,50p' packages/luften_eph.yaml

# 3. Fix duplicate names by making them unique with specific prefixes
echo "Fixing duplicate names..."

# Fix "Heating Tracker" duplicates (likely in heating_analytics_package.yaml)
sed -i 's/name: "Heating Tracker"/name: "Heating Analytics Tracker"/g' packages/heating_analytics_package.yaml
sed -i 's/name: Heating Tracker/name: "Heating Analytics Tracker"/g' packages/heating_analytics_package.yaml

# Fix "Lüften Dynamic" duplicates (likely in luften_dynamic.yaml)
# Make each instance unique by adding context
sed -i '0,/name: "Lüften Dynamic"/{s/name: "Lüften Dynamic"/name: "Lüften Dynamic - Humidity"/}' packages/luften_dynamic.yaml
sed -i '0,/name: "Lüften Dynamic"/{s/name: "Lüften Dynamic"/name: "Lüften Dynamic - Temperature"/}' packages/luften_dynamic.yaml
sed -i 's/name: "Lüften Dynamic"/name: "Lüften Dynamic - Control"/g' packages/luften_dynamic.yaml

# Alternative approach - add line numbers to make them unique
awk '/name: "Lüften Dynamic"/ { $0 = "    name: \"Lüften Dynamic - " ++count "\"" } 1' packages/luften_dynamic.yaml > packages/luften_dynamic.yaml.tmp && mv packages/luften_dynamic.yaml.tmp packages/luften_dynamic.yaml

# Fix "Lüften Castle Ventilation" duplicates (likely in luften_eph.yaml)
sed -i '0,/name: "Lüften Castle Ventilation"/{s/name: "Lüften Castle Ventilation"/name: "Lüften Castle Ventilation - Control"/}' packages/luften_eph.yaml
sed -i 's/name: "Lüften Castle Ventilation"/name: "Lüften Castle Ventilation - Monitor"/g' packages/luften_eph.yaml

# 4. Additional fixes for common issues
echo "Applying additional name uniqueness fixes..."

# Fix the generic names we identified earlier
sed -i 's/name: Comfort Temp (Day)/name: "Lüften Comfort Temp (Day)"/g' packages/luften_eph.yaml
sed -i 's/name: Comfort Temp (Night)/name: "Lüften Comfort Temp (Night)"/g' packages/luften_eph.yaml
sed -i 's/name: Dew Point Sensitivity/name: "Lüften Dew Point Sensitivity"/g' packages/luften_eph.yaml

# Add prefixes to heating analytics names
sed -i 's/name: Zone ONE/name: "Heating Analytics - Zone ONE/g' packages/heating_analytics_package.yaml

echo "=== CHECKING FOR REMAINING DUPLICATES ==="
echo "Remaining duplicate names (should be empty):"
grep -h "^[[:space:]]*name:" packages/*.yaml | sort | uniq -c | sort -nr | grep -v "1 "

echo "=== VALIDATING YAML SYNTAX ==="
for file in packages/*.yaml; do
    echo "Checking $file..."
    python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null && echo "✓ $file - OK" || echo "✗ $file - YAML ERROR"
done

echo "=== NEXT STEPS ==="
echo "1. Run: ha core check"
echo "2. If successful: ha core restart"
echo "3. Check HA logs for any remaining issues"
echo "4. Test EPH integration: source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py status ONE"

echo "Fix script completed!"