# Quick YAML Error Fixes

## Run this to get detailed error info:

```bash
cd /root/config

# Check heating_analytics_package.yaml for detailed error
python3 -c "
import yaml
try:
    yaml.safe_load(open('packages/heating_analytics_package.yaml'))
    print('OK')
except yaml.YAMLError as e:
    print('YAML Error:', e)
    if hasattr(e, 'problem_mark'):
        print('Line:', e.problem_mark.line + 1, 'Column:', e.problem_mark.column + 1)
"

# Check luften_eph.yaml for detailed error  
python3 -c "
import yaml
try:
    yaml.safe_load(open('packages/luften_eph.yaml'))
    print('OK')
except yaml.YAMLError as e:
    print('YAML Error:', e)
    if hasattr(e, 'problem_mark'):
        print('Line:', e.problem_mark.line + 1, 'Column:', e.problem_mark.column + 1)
"
```

## Common Quick Fixes:

### Fix 1: Missing quotes around names
```bash
cd /root/config/packages
sed -i 's/name: \([^"]\)/name: "\1/g' heating_analytics_package.yaml
sed -i 's/name: \([^"]\)/name: "\1/g' luften_eph.yaml
```

### Fix 2: Fix line 46 in luften_eph.yaml specifically
```bash
# Replace line 46 with a properly formatted line
sed -i '46s/.*/    name: "Lüften Dew Point Sensitivity"/' packages/luften_eph.yaml
```

### Fix 3: Fix missing values (empty colons)
```bash
sed -i 's/:$/: null/g' packages/heating_analytics_package.yaml
sed -i 's/:$/: null/g' packages/luften_eph.yaml
```

### Fix 4: Remove tabs and fix indentation
```bash
sed -i 's/\t/    /g' packages/heating_analytics_package.yaml  
sed -i 's/\t/    /g' packages/luften_eph.yaml
```

## Alternative: Manual inspection

Look at the exact problematic lines:

```bash
# For heating_analytics_package.yaml - check around input_number
sed -n '20,30p' packages/heating_analytics_package.yaml

# For luften_eph.yaml - check around line 46
sed -n '44,48p' packages/luften_eph.yaml
```

## Expected fixes needed:

1. **luften_eph.yaml line 46**: Likely `name: Dew Point Sensitivity (°C diff trigger)` needs quotes around the value
2. **heating_analytics_package.yaml**: Likely missing quotes around some name values or malformed YAML structure

## After fixes, test:
```bash
ha core check
```

If still errors, run the detailed diagnostic script and share the exact error messages.