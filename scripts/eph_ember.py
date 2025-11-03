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
        print("\nActions:")
        print("  list_zones              - List all zones")
        print("  get_temp <zone>         - Get current temperature")
        print("  get_target <zone>       - Get target temperature")  
        print("  set_temp <zone> <temp>  - Set target temperature")
        print("  get_status <zone>       - Get zone status (on/off)")
        print("  set_advance <zone> <on/off> - Set zone advance")
        print("\nSet credentials with environment variables:")
        print("  export EPH_EMAIL='your-email@example.com'")
        print("  export EPH_PASSWORD='your-password'")
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
            print("Run without arguments to see usage information.")
            sys.exit(1)
    except IndexError:
        print(f"Missing required arguments for action: {action}")
        print("Run without arguments to see usage information.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)