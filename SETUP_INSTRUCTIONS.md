# EPH Controls Helper Script Setup for Home Assistant

## 1. Copy Script to Home Assistant

```bash
# Copy the helper script to your Home Assistant scripts directory
scp /Users/paulolphert/Ember/pyephember/eph_helper.py hassio@homeassistant:/root/config/scripts/
```

## 2. Set Environment Variables in Home Assistant

Add to your `/root/config/scripts/.env` file (create if doesn't exist):

```bash
# EPH Controls credentials
export EPH_USERNAME="your_eph_username"
export EPH_PASSWORD="your_eph_password"
```

## 3. Home Assistant Configuration Examples

### Command Line Sensors

Add to your `configuration.yaml`:

```yaml
# EPH Controls Sensors
sensor:
  # Current temperature
  - platform: command_line
    name: "EPH Current Temperature"
    command: "source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py temperature ONE"
    unit_of_measurement: "°C"
    device_class: temperature
    scan_interval: 60
    
  # Target temperature  
  - platform: command_line
    name: "EPH Target Temperature"
    command: "source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py target ONE"
    unit_of_measurement: "°C"
    device_class: temperature
    scan_interval: 60
    
  # Zone active status
  - platform: command_line
    name: "EPH Zone Active"
    command: "source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py active ONE"
    scan_interval: 60

# Binary sensors for heating status
binary_sensor:
  - platform: command_line
    name: "EPH Boiler On"
    command: "source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py boiler ONE"
    payload_on: "true"
    payload_off: "false"
    scan_interval: 60
```

### Shell Commands for Control

```yaml
# Shell commands for EPH control
shell_command:
  eph_set_temperature: "source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py set_target ONE {{ temperature }}"
  eph_get_status: "source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py status ONE"
```

### Template Climate Entity (Advanced)

```yaml
# Template climate entity
climate:
  - platform: generic_thermostat
    name: "EPH Thermostat"
    heater: switch.eph_heating  # You'll need to create this switch
    target_sensor: sensor.eph_current_temperature
    min_temp: 5
    max_temp: 30
    ac_mode: false
    target_temp: 19
    cold_tolerance: 0.3
    hot_tolerance: 0
    initial_hvac_mode: "heat"
```

## 4. Automation Examples

### Temperature Control Automation

```yaml
automation:
  - alias: "Set EPH Temperature from Input"
    trigger:
      - platform: state
        entity_id: input_number.target_temperature
    action:
      - service: shell_command.eph_set_temperature
        data:
          temperature: "{{ states('input_number.target_temperature') | float }}"
```

### Input Number for Temperature Control

```yaml
input_number:
  target_temperature:
    name: "Target Temperature"
    min: 5
    max: 30
    step: 0.5
    unit_of_measurement: "°C"
    icon: mdi:thermometer
```

## 5. Testing Commands

Test the script manually on Home Assistant:

```bash
# SSH into Home Assistant
ssh hassio@homeassistant

# Source environment variables
source /root/config/scripts/.env

# Test commands
python3 /root/config/scripts/eph_helper.py zones
python3 /root/config/scripts/eph_helper.py temperature ONE
python3 /root/config/scripts/eph_helper.py target ONE
python3 /root/config/scripts/eph_helper.py status ONE
```

## 6. Dashboard Card Example

```yaml
# Lovelace card
type: thermostat
entity: climate.eph_thermostat
name: "EPH Heating"
```

Or a custom card:

```yaml
type: entities
title: "EPH Controls"
entities:
  - entity: sensor.eph_current_temperature
    name: "Current Temperature"
  - entity: sensor.eph_target_temperature  
    name: "Target Temperature"
  - entity: binary_sensor.eph_boiler_on
    name: "Boiler Status"
  - entity: input_number.target_temperature
    name: "Set Temperature"
```

## 7. Backup Your Existing Integration

Since you have a working custom component, keep it as backup:

```bash
# Backup existing component
cp -r /root/config/custom_components/eph_ember /root/config/custom_components/eph_ember_backup
```

## 8. Zone Names

The script currently maps:
- Display name: "ONE" 
- Zone ID: "0fed0b70485649a3af8c8b0e0a12ce57"

If you have multiple zones, the script will auto-discover them. Use the `zones` command to list available zones:

```bash
python3 /root/config/scripts/eph_helper.py zones
```

## Installation Summary

1. Copy `eph_helper.py` to `/root/config/scripts/`
2. Create `.env` file with EPH credentials  
3. Add sensors/commands to `configuration.yaml`
4. Restart Home Assistant
5. Test functionality
6. Create dashboard cards

This gives you full EPH control through Home Assistant with the working zone ID mapping we discovered!