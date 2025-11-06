#!/bin/bash
# Emergency Fix for heating_analytics_package.yaml YAML Structure Error
# Error: line 9 column 5 - expected <block end>, but found '<scalar>' at line 19 column 12

cd /root/config

echo "=== EMERGENCY YAML FIX FOR heating_analytics_package.yaml ==="

# Create backup
cp packages/heating_analytics_package.yaml packages/heating_analytics_package.yaml.emergency_backup

echo "Current problematic section (lines 5-25):"
sed -n '5,25p' packages/heating_analytics_package.yaml | cat -n

echo ""
echo "=== ANALYZING THE EXACT STRUCTURE PROBLEM ==="

# The error suggests that at line 9, YAML expects a block to end, but at line 19 column 12
# there's unexpected content. This usually means:
# 1. Missing colon after a key
# 2. Wrong indentation level
# 3. Content that should be indented isn't
# 4. A block that should be closed isn't

# Let's look at the specific lines with character positions
echo "Line 9 with character positions:"
sed -n '9p' packages/heating_analytics_package.yaml | cat -A

echo "Line 19 with character positions:"
sed -n '19p' packages/heating_analytics_package.yaml | cat -A

echo ""
echo "=== COMMON FIXES FOR THIS ERROR PATTERN ==="

# Fix 1: Ensure line 9 has proper structure (likely a key without proper colon or value)
# Fix 2: Ensure line 19 column 12 doesn't have unexpected content

# Get the exact content to understand the issue
echo "Examining counter section structure..."

# The error pattern suggests this is likely in the counter section
# Let's apply targeted fixes:

# 1. Fix any lines that should end with colons but don't
sed -i '9s/$//' packages/heating_analytics_package.yaml  # Remove any trailing chars on line 9
sed -i '9s/^  \([a-zA-Z_][a-zA-Z0-9_]*\)$/  \1:/' packages/heating_analytics_package.yaml

# 2. Fix line 19 column 12 issue - likely indentation or missing structure
# This is often a name: value that's not properly indented or quoted
sed -i '19s/^            /    /' packages/heating_analytics_package.yaml  # Fix over-indentation
sed -i '19s/^        /    /' packages/heating_analytics_package.yaml      # Fix double-indentation

# 3. Ensure proper YAML structure for counter section
# Replace any malformed counter entries
sed -i '/^counter:/,/^[a-zA-Z]/ {
    s/^  \([a-zA-Z_][a-zA-Z0-9_]*\)$/  \1:/
    s/^    name: \([^"]\)/    name: "\1/
    s/^    name: "\([^"]*\)$/    name: "\1"/
}' packages/heating_analytics_package.yaml

echo ""
echo "=== TESTING THE FIX ==="
python3 -c "
import yaml
try:
    with open('packages/heating_analytics_package.yaml', 'r') as f:
        yaml.safe_load(f)
    print('✓ heating_analytics_package.yaml - FIXED!')
except yaml.YAMLError as e:
    print('✗ Still has error:', e)
    if hasattr(e, 'problem_mark'):
        print('  Line:', e.problem_mark.line + 1, 'Column:', e.problem_mark.column + 1)
"

echo ""
echo "=== IF STILL BROKEN - EMERGENCY CONTENT REPLACEMENT ==="
echo "If the above didn't work, we can replace the problematic section with a minimal working version:"

# Create a minimal working counter section if the fix above doesn't work
cat > /tmp/counter_fix.yaml << 'EOF'
counter:
  zone_one_heating_cycles_today:
    name: "Heating Analytics - Zone ONE Cycles"
    icon: mdi:counter
EOF

echo "Emergency replacement available in /tmp/counter_fix.yaml"
echo "If needed, manually replace the counter section in heating_analytics_package.yaml"

echo ""
echo "=== FINAL TEST ==="
echo "Run this to test the complete configuration:"
echo "ha core check"