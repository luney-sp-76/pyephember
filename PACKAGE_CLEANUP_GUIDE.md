# Package Conflict Resolution Guide

## Problem Analysis
The configuration warnings show duplicate keys from packages:
- `heating_analytics_package` has duplicate: counter 'name', input_datetime 'name', input_number 'name'
- `luften` package has duplicate: input_number 'name'

## Solution Strategy

### Option 1: Temporarily Disable Packages (Immediate Fix)
Use the `fixed_configuration.yaml` I created which:
1. Comments out the packages line: `# packages: !include_dir_named packages`
2. Renames conflicting entities to unique names
3. Moves all functionality into main configuration.yaml

### Option 2: Fix Package Conflicts (Long-term Solution)

#### Step 1: Check Your Packages Directory
```bash
# SSH into Home Assistant
ssh hassio@homeassistant

# List package files
ls -la /root/config/packages/

# Check for conflicts in each package file
grep -n "name:" /root/config/packages/*.yaml
```

#### Step 2: Rename Conflicting Entities
Look for these duplicate entity names in your packages:

**In heating_analytics_package.yaml:**
```yaml
# RENAME THESE:
counter:
  zone_one_heating_cycles_today:  # Change to: zone_one_heating_cycles
input_datetime:
  zone_one_heating_start:         # Change to: zone_one_heating_start_time
input_number:
  zone_one_total_heating_time_today:  # Change to: zone_one_total_heating_time
```

**In luften.yaml:**
```yaml
# RENAME THIS:
input_number:
  target_temperature:             # Change to: luften_target_temperature
```

#### Step 3: Update Entity References
After renaming entities, update all references in:
- Dashboard YAML files
- Automations
- Other template sensors that reference the old names

## Quick Fix Implementation

### 1. Use Fixed Configuration
```bash
# Backup current config
ssh hassio@homeassistant
cp /root/config/configuration.yaml /root/config/configuration.yaml.backup

# Copy fixed configuration
scp /Users/paulolphert/Ember/pyephember/fixed_configuration.yaml hassio@homeassistant:/root/config/configuration.yaml
```

### 2. Test Configuration
```bash
# Check configuration
ha core check

# If valid, restart
ha core restart
```

### 3. Re-enable Packages Later
Once you've fixed the package conflicts:
1. Uncomment the packages line: `packages: !include_dir_named packages`
2. Remove duplicate entities from main configuration.yaml
3. Test and restart

## Key Changes Made in Fixed Config

### Entity Name Changes:
- `input_number.target_temperature` → `input_number.eph_target_temperature`
- `input_number.zone_one_total_heating_time_today` → `input_number.zone_one_total_heating_time`
- `counter.zone_one_heating_cycles_today` → `counter.zone_one_heating_cycles`
- `input_datetime.zone_one_heating_start` → `input_datetime.zone_one_heating_start_time`

### Dashboard Updates Needed:
Update your dashboard to use the new entity names:
- `counter.zone_one_heating_cycles_today` → `counter.zone_one_heating_cycles`
- `input_number.zone_one_total_heating_time_today` → `input_number.zone_one_total_heating_time`
- `input_datetime.zone_one_heating_start` → `input_datetime.zone_one_heating_start_time`

## Verification Steps

1. **Configuration Valid**: No more duplicate key warnings
2. **EPH Integration Working**: Sensors updating with temperature data
3. **Dashboard Loading**: No template errors
4. **Analytics Working**: Heating cycle counting and efficiency calculations

## Recovery Plan
If anything breaks:
```bash
# Restore backup
ssh hassio@homeassistant
cp /root/config/configuration.yaml.backup /root/config/configuration.yaml
ha core restart
```

The fixed configuration should resolve all duplicate key issues and get your EPH integration working properly!