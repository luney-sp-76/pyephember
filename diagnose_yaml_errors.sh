#!/bin/bash
# Detailed YAML Error Diagnostic and Fix Script

cd /root/config

echo "=== DETAILED YAML ERROR DIAGNOSIS ==="

# Function to get detailed YAML error
check_yaml_detailed() {
    local file="$1"
    echo "Checking $file in detail..."
    python3 -c "
import yaml
import sys
try:
    with open('$file', 'r') as f:
        yaml.safe_load(f)
    print('✓ $file - OK')
except yaml.YAMLError as e:
    print('✗ $file - YAML ERROR:')
    print(f'  Error: {e}')
    if hasattr(e, 'problem_mark'):
        mark = e.problem_mark
        print(f'  Line: {mark.line + 1}, Column: {mark.column + 1}')
except Exception as e:
    print('✗ $file - OTHER ERROR:')
    print(f'  Error: {e}')
"
    echo ""
}

# Check the problematic files in detail
check_yaml_detailed "packages/heating_analytics_package.yaml"
check_yaml_detailed "packages/luften_eph.yaml"

echo "=== EXAMINING PROBLEMATIC LINE RANGES ==="

echo "--- heating_analytics_package.yaml around potential problem areas ---"
echo "Lines 1-10:"
head -10 packages/heating_analytics_package.yaml
echo ""
echo "Lines around input_number (23):"
sed -n '20,30p' packages/heating_analytics_package.yaml
echo ""

echo "--- luften_eph.yaml around line 46 (known problem) ---"
echo "Lines 40-50:"
sed -n '40,50p' packages/luften_eph.yaml
echo ""

echo "=== COMMON YAML FIXES ==="
echo "Now applying common YAML fixes..."

# Create backups first
cp packages/heating_analytics_package.yaml packages/heating_analytics_package.yaml.backup
cp packages/luften_eph.yaml packages/luften_eph.yaml.backup

# Fix common YAML issues

# 1. Fix missing quotes around problematic values
echo "Fixing missing quotes..."
sed -i 's/name: \([^"]\)/name: "\1/g' packages/heating_analytics_package.yaml
sed -i 's/name: \([^"]\)/name: "\1/g' packages/luften_eph.yaml

# 2. Fix unterminated quotes (add closing quotes if missing)
sed -i 's/name: "[^"]*$/&"/g' packages/heating_analytics_package.yaml
sed -i 's/name: "[^"]*$/&"/g' packages/luften_eph.yaml

# 3. Fix specific issues around line 46 in luften_eph.yaml
# This is likely the "Dew Point Sensitivity" line
sed -i '46s/.*/    name: "Lüften Dew Point Sensitivity"/' packages/luften_eph.yaml

# 4. Fix any lines that end with colons but no values
sed -i 's/:$/: ""/g' packages/heating_analytics_package.yaml
sed -i 's/:$/: ""/g' packages/luften_eph.yaml

# 5. Fix indentation issues (ensure proper 2-space or 4-space indentation)
# Convert tabs to spaces
sed -i 's/\t/    /g' packages/heating_analytics_package.yaml
sed -i 's/\t/    /g' packages/luften_eph.yaml

echo "=== RE-CHECKING YAML SYNTAX AFTER FIXES ==="
check_yaml_detailed "packages/heating_analytics_package.yaml"
check_yaml_detailed "packages/luften_eph.yaml"

echo "=== FINAL VALIDATION ==="
for file in packages/*.yaml; do
    python3 -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null && echo "✓ $file - OK" || echo "✗ $file - STILL HAS ERRORS"
done

echo ""
echo "=== NEXT STEPS ==="
echo "If files still have errors, examine the detailed output above"
echo "Look for lines with missing colons, quotes, or improper indentation"
echo "Manual fixes may be needed for complex structural issues"