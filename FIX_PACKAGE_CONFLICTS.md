# Fix Package Duplicate Key Conflicts - Step by Step Guide

## Problem
Your packages have duplicate entity `name:` fields causing HA to fail with "integration 'input_number' has duplicate key 'name'"

## Root Cause
Looking at the name fields from your packages, there are likely duplicate display names or conflicts. The main issue is that multiple packages may be defining entities with the same display names.

## Quick Fix Strategy

### Step 1: Backup and Use Clean Config
1. **Backup your current config:**
   ```bash
   cd /root/config
   cp configuration.yaml configuration.yaml.backup_$(date +%Y%m%d_%H%M)
   cp -r packages packages.backup_$(date +%Y%m%d_%H%M)
   ```

2. **Replace your configuration.yaml** with the clean version:
   - Copy the contents of `clean_config_packages_enabled.yaml` (from this workspace) to `/root/config/configuration.yaml`
   - This removes all input_number/counter/input_datetime from main config to avoid conflicts

### Step 2: Fix Package Name Conflicts
Based on the analysis, the most likely culprits are display name conflicts. Here are the specific changes needed:

#### A) Fix luften_eph.yaml
The names "Comfort Temp (Day)" and "Comfort Temp (Night)" might be too generic. Change them:

**Find this in `/root/config/packages/luften_eph.yaml`:**
```yaml
input_number:
  luften_castle_comfort_temp_day:
    name: Comfort Temp (Day)
```

**Change to:**
```yaml
input_number:
  luften_castle_comfort_temp_day:
    name: "Lüften Comfort Temp (Day)"
```

**And:**
```yaml
  luften_castle_comfort_temp_night:
    name: Comfort Temp (Night)
```

**Change to:**
```yaml
  luften_castle_comfort_temp_night:
    name: "Lüften Comfort Temp (Night)"
```

#### B) Check for Duplicate Display Names
Run this command to find any duplicate display names:
```bash
grep -h "^[[:space:]]*name:" /root/config/packages/*.yaml | sort | uniq -c | sort -nr | grep -v "1 "
```

If this shows any duplicates (lines starting with numbers > 1), those need to be made unique.

### Step 3: Alternative - Simple Rename Script
If you want to automate the fix, create this script on your HA host:

```bash
cat > /root/config/fix_package_names.sh << 'EOF'
#!/bin/bash
cd /root/config/packages

# Backup packages
cp -r . ../packages.backup_$(date +%Y%m%d_%H%M)

# Fix luften_eph.yaml names to be unique
sed -i 's/name: Comfort Temp (Day)/name: "Lüften Comfort Temp (Day)"/' luften_eph.yaml
sed -i 's/name: Comfort Temp (Night)/name: "Lüften Comfort Temp (Night)"/' luften_eph.yaml
sed -i 's/name: Dew Point Sensitivity/name: "Lüften Dew Point Sensitivity"/' luften_eph.yaml

# Fix any other potential conflicts by adding package prefixes to display names
sed -i 's/name: Zone ONE/name: "Heating Analytics - Zone ONE/g' heating_analytics_package.yaml

echo "Package names fixed. Run 'ha core check' to validate."
EOF

chmod +x /root/config/fix_package_names.sh
/root/config/fix_package_names.sh
```

### Step 4: Test and Deploy
1. **Copy the clean configuration:**
   ```bash
   # Replace your configuration.yaml with the clean version (remove input_number conflicts)
   # [Copy clean_config_packages_enabled.yaml contents to /root/config/configuration.yaml]
   ```

2. **Validate configuration:**
   ```bash
   ha core check
   # or
   hass --script check_config -c /root/config
   ```

3. **If validation passes:**
   ```bash
   ha core restart
   ```

### Step 5: Verify Everything Works
1. **Check logs for errors:**
   ```bash
   ha core logs
   ```

2. **Test EPH integration:**
   ```bash
   source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py status ONE
   ```

3. **Check entities in HA UI:**
   - Go to Developer Tools > States
   - Look for your lüften and heating entities
   - Confirm no "unknown" or "unavailable" states

## If You Still Get Errors

If you still get duplicate key errors after the above changes, please run:
```bash
# Find the exact duplicate names
grep -h "^[[:space:]]*name:" /root/config/packages/*.yaml | sort | uniq -c | sort -nr | head -10
```

And share the output. I can then provide specific renames for the exact duplicates found.

## Quick Recovery
If anything breaks, you can always restore:
```bash
cd /root/config
cp configuration.yaml.backup_* configuration.yaml
cp -r packages.backup_*/* packages/
ha core restart
```