# PyEphEmber Home Assistant Integration Guide

This guide shows you how to integrate your EPH Controls Ember heating system with Home Assistant using the PyEphEmber library.

## 🏠 Overview

You can integrate EPH Ember with Home Assistant in several ways:
1. **Custom Component** (Recommended) - Full integration with climate entities
2. **Command Line Climate** - Simple sensor/switch setup
3. **Python Scripts** - Advanced automation scripts

## 🚀 Method 1: Custom Component (Recommended)

### Step 1: Install PyEphEmber in Home Assistant

**Option A: Using HACS (Home Assistant Community Store)** ⭐ **RECOMMENDED**
1. Install HACS if you haven't already
2. Search for "EPH Ember" in HACS integrations
3. Install the integration
4. **✅ If you just installed via HACS, see [QUICK_SETUP_AFTER_HACS.md](QUICK_SETUP_AFTER_HACS.md) for immediate next steps!**

**Option B: Manual Installation**
```bash
# SSH into your Home Assistant system
cd /config
mkdir -p custom_components/eph_ember
```

### Step 2: Create the Custom Component

Create the integration files:

## 📦 Method 2: Command Line Sensors (Easiest)

This method uses Home Assistant's command line integration to create sensors and switches for your EPH zones.

### Step 1: Install PyEphEmber

First, install PyEphEmber in your Home Assistant environment:

```bash
# SSH into Home Assistant
# If using Home Assistant OS/Supervised:
docker exec -it homeassistant bash
pip install pyephember

# If using Home Assistant Container:
pip install pyephember

# If using Home Assistant Core:
pip3 install pyephember
```

### Step 2: Create Helper Scripts

Create `/config/scripts/eph_ember.py`:

```python
#!/usr/bin/env python3
"""
EPH Ember helper script for Home Assistant
Usage: python3 eph_ember.py <action> <zone_name> [value]
"""
import sys
import os
from pyephember.pyephember import EphEmber

# Configuration - Store credentials as environment variables
EMAIL = os.environ.get('EPH_EMAIL', 'your-email@example.com')
PASSWORD = os.environ.get('EPH_PASSWORD', 'your-password')

def get_ember_client():
    """Get authenticated EPH Ember client"""
    return EphEmber(EMAIL, PASSWORD)

def get_temperature(zone_name):
    """Get current temperature for a zone"""
    ember = get_ember_client()
    return ember.get_zone_temperature(zone_name)

def get_target_temperature(zone_name):
    """Get target temperature for a zone"""
    ember = get_ember_client()
    return ember.get_zone_target_temperature(zone_name)

def set_temperature(zone_name, temperature):
    """Set target temperature for a zone"""
    ember = get_ember_client()
    ember.set_zone_target_temperature(zone_name, float(temperature))
    return f"Set {zone_name} to {temperature}°C"

def get_zone_status(zone_name):
    """Get zone active status"""
    ember = get_ember_client()
    return "on" if ember.is_zone_active(zone_name) else "off"

def set_zone_advance(zone_name, state):
    """Set zone advance (on/off)"""
    ember = get_ember_client()
    advance = state.lower() in ['on', 'true', '1']
    ember.set_zone_advance(zone_name, advance)
    return f"Zone {zone_name} advance: {'on' if advance else 'off'}"

def list_zones():
    """List all available zones"""
    ember = get_ember_client()
    return ','.join(ember.get_zone_names())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 eph_ember.py <action> <zone_name> [value]")
        sys.exit(1)
    
    action = sys.argv[1]
    
    try:
        if action == 'list_zones':
            print(list_zones())
        elif action == 'get_temp':
            zone_name = sys.argv[2]
            print(get_temperature(zone_name))
        elif action == 'get_target':
            zone_name = sys.argv[2]
            print(get_target_temperature(zone_name))
        elif action == 'set_temp':
            zone_name = sys.argv[2]
            temperature = sys.argv[3]
            print(set_temperature(zone_name, temperature))
        elif action == 'get_status':
            zone_name = sys.argv[2]
            print(get_zone_status(zone_name))
        elif action == 'set_advance':
            zone_name = sys.argv[2]
            state = sys.argv[3]
            print(set_zone_advance(zone_name, state))
        else:
            print(f"Unknown action: {action}")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

### Step 3: Set Environment Variables

Add to `/config/configuration.yaml`:

```yaml
# EPH Ember Environment Variables
homeassistant:
  # ... other config ...
  
# Set environment variables for credentials
shell_command:
  set_eph_credentials: 'export EPH_EMAIL="your-email@example.com" && export EPH_PASSWORD="your-password"'
```

### Step 4: Configure Sensors and Climate Entities

Add to `/config/configuration.yaml`:

```yaml
# EPH Ember Sensors
sensor:
  # Living Room Temperature
  - platform: command_line
    name: "Living Room Temperature"
    command: 'cd /config && python3 scripts/eph_ember.py get_temp "Living Room"'
    unit_of_measurement: "°C"
    scan_interval: 60
    
  - platform: command_line
    name: "Living Room Target Temperature"
    command: 'cd /config && python3 scripts/eph_ember.py get_target "Living Room"'
    unit_of_measurement: "°C"
    scan_interval: 60
  
  # Add more zones as needed
  - platform: command_line
    name: "Bedroom Temperature"
    command: 'cd /config && python3 scripts/eph_ember.py get_temp "Bedroom"'
    unit_of_measurement: "°C"
    scan_interval: 60

# EPH Ember Climate Control
climate:
  - platform: generic_thermostat
    name: "Living Room Thermostat"
    heater: switch.living_room_heating
    target_sensor: sensor.living_room_temperature
    min_temp: 10
    max_temp: 30
    ac_mode: false
    target_temp: 20
    cold_tolerance: 0.3
    hot_tolerance: 0

# EPH Ember Switches  
switch:
  - platform: command_line
    switches:
      living_room_heating:
        command_on: 'cd /config && python3 scripts/eph_ember.py set_advance "Living Room" on'
        command_off: 'cd /config && python3 scripts/eph_ember.py set_advance "Living Room" off'
        command_state: 'cd /config && python3 scripts/eph_ember.py get_status "Living Room"'
        value_template: '{{ value == "on" }}'
```

## 🎛️ Method 3: Advanced Python Scripts Integration

### Step 1: Create Advanced Control Script

Create `/config/python_scripts/eph_ember_control.py`:

```python
"""
Advanced EPH Ember control for Home Assistant Python Scripts
"""
import json

# Get parameters from Home Assistant
zone_name = data.get('zone_name', 'Living Room')
action = data.get('action', 'get_temp')
value = data.get('value', None)

# Import and use EPH Ember
try:
    from pyephember.pyephember import EphEmber
    
    # Use secrets for credentials
    email = hass.services.call('keyring', 'get', {'service': 'eph_ember', 'username': 'email'})
    password = hass.services.call('keyring', 'get', {'service': 'eph_ember', 'username': 'password'})
    
    ember = EphEmber(email, password)
    
    if action == 'set_temperature':
        ember.set_zone_target_temperature(zone_name, float(value))
        result = f"Set {zone_name} to {value}°C"
    elif action == 'set_boost':
        boost_temp = float(value)
        hours = data.get('hours', 2)
        ember.set_zone_boost(zone_name, boost_temp, hours)
        result = f"Boosted {zone_name} to {boost_temp}°C for {hours}h"
    elif action == 'get_all_info':
        current = ember.get_zone_temperature(zone_name)
        target = ember.get_zone_target_temperature(zone_name)
        active = ember.is_zone_active(zone_name)
        result = {
            'current_temp': current,
            'target_temp': target,
            'is_active': active
        }
    else:
        result = "Unknown action"
    
    # Set the result in Home Assistant
    hass.states.set(f'sensor.eph_ember_result', json.dumps(result))
    
except Exception as e:
    logger.error(f"EPH Ember error: {e}")
    hass.states.set('sensor.eph_ember_result', f"Error: {e}")
```

### Step 2: Create Automations

Add to `/config/automations.yaml`:

```yaml
# EPH Ember Automations
- alias: "EPH Ember - Morning Heat Boost"
  trigger:
    platform: time
    at: "06:30:00"
  condition:
    condition: time
    weekday:
      - mon
      - tue
      - wed
      - thu
      - fri
  action:
    - service: python_script.eph_ember_control
      data:
        zone_name: "Living Room"
        action: "set_boost"
        value: 22
        hours: 1

- alias: "EPH Ember - Energy Saving Mode"
  trigger:
    platform: time
    at: "22:00:00"
  action:
    - service: python_script.eph_ember_control
      data:
        zone_name: "Living Room"
        action: "set_temperature"
        value: 18
```

## 📊 Dashboard Configuration

### Lovelace Dashboard Cards

Add these cards to your dashboard:

```yaml
# EPH Ember Dashboard
type: vertical-stack
cards:
  - type: entities
    title: EPH Ember Heating
    entities:
      - sensor.living_room_temperature
      - sensor.living_room_target_temperature
      - switch.living_room_heating
      
  - type: thermostat
    entity: climate.living_room_thermostat
    
  - type: horizontal-stack
    cards:
      - type: button
        tap_action:
          action: call-service
          service: python_script.eph_ember_control
          service_data:
            zone_name: "Living Room"
            action: "set_boost"
            value: 22
            hours: 2
        name: "Boost 2h"
        icon: mdi:fire
        
      - type: button
        tap_action:
          action: call-service
          service: python_script.eph_ember_control
          service_data:
            zone_name: "Living Room"
            action: "set_temperature"
            value: 16
        name: "Eco Mode"
        icon: mdi:leaf
```

## 🔧 Configuration Examples

### Multi-Zone Setup

For multiple zones, create template sensors:

```yaml
# Template sensors for all zones
template:
  - sensor:
      - name: "All Zone Temperatures"
        state: >
          {% set zones = ['Living Room', 'Bedroom', 'Kitchen'] %}
          {% set temps = [] %}
          {% for zone in zones %}
            {% set entity = 'sensor.' + zone.lower().replace(' ', '_') + '_temperature' %}
            {% if states(entity) != 'unavailable' %}
              {% set temps = temps + [zone + ': ' + states(entity) + '°C'] %}
            {% endif %}
          {% endfor %}
          {{ temps | join(', ') }}
```

### Advanced Automations

```yaml
# Smart heating based on occupancy
- alias: "Smart EPH Heating"
  trigger:
    - platform: state
      entity_id: binary_sensor.living_room_occupancy
      to: 'on'
  condition:
    - condition: numeric_state
      entity_id: sensor.living_room_temperature
      below: 19
  action:
    - service: python_script.eph_ember_control
      data:
        zone_name: "Living Room"
        action: "set_temperature"
        value: 21
```

## 🔒 Security & Best Practices

### 1. Secure Credential Storage

**Option A: Environment Variables**
```bash
# Add to your system environment
export EPH_EMAIL="your-email@example.com"
export EPH_PASSWORD="your-password"
```

**Option B: Home Assistant Secrets**
```yaml
# secrets.yaml
eph_email: "your-email@example.com"
eph_password: "your-password"

# configuration.yaml
shell_command:
  eph_set_temp: 'python3 /config/scripts/eph_ember.py set_temp "{{ zone }}" {{ temp }} --email "!secret eph_email" --password "!secret eph_password"'
```

### 2. Error Handling

```yaml
# Add error sensors
sensor:
  - platform: command_line
    name: "EPH Ember Status"
    command: 'cd /config && python3 scripts/eph_ember.py list_zones'
    scan_interval: 300
    value_template: >
      {% if value != '' %}
        online
      {% else %}
        offline  
      {% endif %}
```

## 🚀 Quick Setup Script

Create `/config/setup_eph_ember.sh`:

```bash
#!/bin/bash
# Quick setup script for EPH Ember integration

echo "🔥 Setting up EPH Ember integration..."

# Create directories
mkdir -p /config/scripts
mkdir -p /config/python_scripts

# Download helper script
echo "📥 Creating helper script..."
cat > /config/scripts/eph_ember.py << 'EOF'
# [Insert the eph_ember.py script content here]
EOF

chmod +x /config/scripts/eph_ember.py

# Install PyEphEmber
echo "📦 Installing PyEphEmber..."
pip install pyephember

echo "✅ Setup complete!"
echo "📝 Next steps:"
echo "1. Edit /config/scripts/eph_ember.py with your credentials"
echo "2. Add sensor configuration to configuration.yaml"
echo "3. Restart Home Assistant"
echo "4. Add dashboard cards"
```

## 🎯 Testing Your Setup

### Test Commands

```bash
# Test the helper script
cd /config
python3 scripts/eph_ember.py list_zones
python3 scripts/eph_ember.py get_temp "Living Room"
python3 scripts/eph_ember.py set_temp "Living Room" 21

# Check Home Assistant logs
tail -f /config/home-assistant.log | grep -i "eph"
```

### Troubleshooting

Common issues and solutions:

1. **Import Error**: `pip install pyephember` in the correct environment
2. **Authentication Failed**: Check email/password in credentials
3. **Zone Not Found**: Use exact zone names from `list_zones`
4. **Timeout Errors**: Increase `scan_interval` values
5. **Permission Denied**: `chmod +x /config/scripts/eph_ember.py`

## 📈 Advanced Features

### Custom Services

Register custom services in `/config/configuration.yaml`:

```yaml
# Custom EPH Ember services
script:
  eph_ember_boost_all:
    alias: "Boost All Zones"
    sequence:
      - service: python_script.eph_ember_control
        data:
          zone_name: "Living Room"
          action: "set_boost"
          value: 22
          hours: 1
      - service: python_script.eph_ember_control
        data:
          zone_name: "Bedroom" 
          action: "set_boost"
          value: 20
          hours: 1

  eph_ember_eco_mode:
    alias: "Enable Eco Mode"
    sequence:
      - service: python_script.eph_ember_control
        data:
          zone_name: "{{ zone }}"
          action: "set_temperature"
          value: 16
```

### Energy Monitoring

```yaml
# Track heating energy usage
sensor:
  - platform: template
    sensors:
      heating_active_zones:
        friendly_name: "Active Heating Zones"
        value_template: >
          {% set zones = ['Living Room', 'Bedroom'] %}
          {% set active = [] %}
          {% for zone in zones %}
            {% set switch = 'switch.' + zone.lower().replace(' ', '_') + '_heating' %}
            {% if is_state(switch, 'on') %}
              {% set active = active + [zone] %}
            {% endif %}
          {% endfor %}
          {{ active | length }}
```

## ✅ Summary

You now have multiple ways to integrate EPH Ember with Home Assistant:

1. **🚀 Quick Start**: Use Method 2 (Command Line) for immediate results
2. **🏗️ Full Integration**: Use Method 1 (Custom Component) for native HA climate entities  
3. **🎛️ Advanced Control**: Use Method 3 (Python Scripts) for complex automations

Choose the method that best fits your technical comfort level and requirements!

### Next Steps:
1. Choose your integration method
2. Set up credentials securely
3. Configure sensors and climate entities
4. Create dashboard cards
5. Add automations for smart heating control

Happy heating! 🔥