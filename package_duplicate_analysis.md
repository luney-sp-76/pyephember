# Package Duplicate Key Analysis & Fix Plan

## Problem Identified
Based on the HA error and package analysis, the issue is likely:
1. Duplicate `name:` fields across different input_number entities in packages
2. Potential conflicts between main config and package entity definitions

## Package Input Numbers Found

### heating_analytics_package.yaml (line 23)
```yaml
input_number:
  zone_one_total_heating_time_today:
    name: Zone ONE Total Heating Time Today
```

### luften.yaml (line 14) 
```yaml
input_number:
  luften_base_minutes_winter:
    name: Lüften Base Minutes (Winter)
  luften_base_minutes_summer:
    name: Lüften Base Minutes (Summer)
  luften_additional_minutes_per_2c_gap:
    name: Extra Minutes per 2°C Dew Point Gap
  # ... more entities
```

### luften_eph.yaml (line 28)
```yaml
input_number:
  luften_castle_comfort_temp_day:
    name: Comfort Temp (Day)
  luften_castle_comfort_temp_night:
    name: Comfort Temp (Night)
  luften_castle_dewpoint_sensitivity:
    name: Dew Point Sensitivity (°C diff trigger)
```

## Root Cause Analysis
The error "integration 'input_number' has duplicate key 'name'" suggests that:
1. Multiple input_number entities have identical `name:` values, OR
2. There are duplicate entity IDs (keys under input_number:), OR
3. The main config conflicts with package definitions

## Solution Strategy
1. **Remove conflicting entities from main config** - Keep only EPH-specific entities
2. **Ensure all package entity IDs are unique** with package prefixes
3. **Ensure all display names are unique** across all packages
4. **Update references** in templates and dashboards

## Recommended Entity Renaming

### Main Config Changes (minimal_config_with_packages.yaml)
- Keep: `input_number.eph_target_temperature_control` (already unique)
- Remove any entities that duplicate package definitions

### Package Prefix Strategy
- `heating_analytics_package.yaml`: prefix with `heating_analytics_`
- `luften.yaml`: prefix with `luften_`  
- `luften_eph.yaml`: prefix with `luften_eph_`
- `influx_heating_config.yaml`: prefix with `influx_heating_`
- `pyephember2_heating_detection.yaml`: prefix with `pyeph_`

### Specific Renames Needed
1. **heating_analytics_package.yaml**:
   - `zone_one_total_heating_time_today` → `heating_analytics_zone_one_total_time`
   - Update name: "Zone ONE Total Heating Time Today" → "Heating Analytics - Zone ONE Total Time"

2. **luften.yaml**: Already have good prefixes, but ensure names are unique:
   - Names appear unique already

3. **luften_eph.yaml**: Entity IDs look good, but check for name conflicts:
   - "Comfort Temp (Day)" might conflict - change to "Lüften Comfort Temp (Day)"
   - "Comfort Temp (Night)" → "Lüften Comfort Temp (Night)"

## Next Steps
1. Create corrected package files with unique entity IDs and names
2. Update main config to remove any conflicting definitions
3. Update references in templates/dashboards
4. Test configuration and restart HA