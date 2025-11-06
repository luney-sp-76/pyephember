# Quick Fix Commands for Package Duplicates and YAML Error

## Immediate Actions Required

### 1. Fix YAML Syntax Error First
The error in `luften_eph.yaml` line 46 needs to be fixed before anything else will work.

**Check the exact problem:**
```bash
cd /root/config
sed -n '40,50p' packages/luften_eph.yaml
```

**Common fixes for line 46:**
- If it's missing a value: `name: Dew Point Sensitivity` → `name: "Dew Point Sensitivity"`
- If it's indentation: ensure it's properly aligned with other entries
- If it's missing quotes: add quotes around the value

### 2. Apply Quick Duplicate Name Fixes
Run these commands to fix the duplicate names:

```bash
cd /root/config/packages

# Fix "Heating Tracker" duplicates - make each unique
sed -i '0,/name: "Heating Tracker"/{s/name: "Heating Tracker"/name: "Heating Analytics Tracker 1"/}' heating_analytics_package.yaml
sed -i '0,/name: "Heating Tracker"/{s/name: "Heating Tracker"/name: "Heating Analytics Tracker 2"/}' heating_analytics_package.yaml  
sed -i 's/name: "Heating Tracker"/name: "Heating Analytics Tracker 3"/g' heating_analytics_package.yaml

# Fix "Lüften Dynamic" duplicates - make each unique
sed -i '0,/name: "Lüften Dynamic"/{s/name: "Lüften Dynamic"/name: "Lüften Dynamic Sensor 1"/}' luften_dynamic.yaml
sed -i '0,/name: "Lüften Dynamic"/{s/name: "Lüften Dynamic"/name: "Lüften Dynamic Sensor 2"/}' luften_dynamic.yaml
sed -i 's/name: "Lüften Dynamic"/name: "Lüften Dynamic Sensor 3"/g' luften_dynamic.yaml

# Fix "Lüften Castle Ventilation" duplicates  
sed -i '0,/name: "Lüften Castle Ventilation"/{s/name: "Lüften Castle Ventilation"/name: "Lüften Castle Ventilation Control"/}' luften_eph.yaml
sed -i 's/name: "Lüften Castle Ventilation"/name: "Lüften Castle Ventilation Monitor"/g' luften_eph.yaml

# Fix other generic names
sed -i 's/name: Comfort Temp (Day)/name: "Lüften Comfort Temp (Day)"/g' luften_eph.yaml
sed -i 's/name: Comfort Temp (Night)/name: "Lüften Comfort Temp (Night)"/g' luften_eph.yaml
```

### 3. Verify No More Duplicates
```bash
grep -h "^[[:space:]]*name:" /root/config/packages/*.yaml | sort | uniq -c | sort -nr | grep -v "1 "
```
This should return empty (no duplicates).

### 4. Check YAML Syntax
```bash
cd /root/config
for file in packages/*.yaml; do
    python3 -c "import yaml; yaml.safe_load(open('$file'))" && echo "✓ $file OK" || echo "✗ $file ERROR"
done
```

### 5. Test Configuration
```bash
ha core check
```

## If Line 46 Error Persists

If you still get the line 46 error, please run:
```bash
sed -n '44,48p' /root/config/packages/luften_eph.yaml
```

And paste the output. The error "expected <block end>, but found '<scalar>'" usually means:
- Missing colon after a key
- Wrong indentation 
- Missing quotes around a value
- Malformed YAML structure

## Alternative: Manual Edit
If the sed commands don't work perfectly, you can manually edit the files:

1. **Edit luften_eph.yaml** around line 46 - ensure proper YAML format
2. **Find and rename the duplicate names**:
   - Change 3 instances of "Heating Tracker" to unique names
   - Change 3 instances of "Lüften Dynamic" to unique names  
   - Change 2 instances of "Lüften Castle Ventilation" to unique names

The key is that each `name:` field must be unique across ALL package files.