#!/usr/bin/env python3
"""
Quick test script to check PyEphEmber2 changes and Home Assistant integration
Run this to see what attributes and states are available from your climate.one entity
"""

import requests
import json
from datetime import datetime

# Home Assistant configuration
HA_URL = "http://homeassistant.local:8123"  # Update with your HA URL
HA_TOKEN = "your_ha_token_here"  # Update with your long-lived access token

def test_climate_entity():
    """Test the climate.one entity to see what's available"""
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get climate.one state
        response = requests.get(f"{HA_URL}/api/states/climate.one", headers=headers)
        if response.status_code == 200:
            data = response.json()
            
            print("=" * 60)
            print("CLIMATE.ONE ENTITY STATE AND ATTRIBUTES")
            print("=" * 60)
            print(f"Entity ID: {data.get('entity_id')}")
            print(f"State: {data.get('state')}")
            print(f"Last Changed: {data.get('last_changed')}")
            print(f"Last Updated: {data.get('last_updated')}")
            
            print("\n" + "=" * 40)
            print("ATTRIBUTES:")
            print("=" * 40)
            attributes = data.get('attributes', {})
            for key, value in sorted(attributes.items()):
                print(f"{key:25} = {value}")
            
            print("\n" + "=" * 40)
            print("HEATING DETECTION ANALYSIS:")
            print("=" * 40)
            
            # Check various heating detection methods
            hvac_action = attributes.get('hvac_action')
            hvac_mode = attributes.get('hvac_mode')
            current_temp = attributes.get('current_temperature')
            target_temp = attributes.get('temperature')
            state = data.get('state')
            
            print(f"Method 1 - HVAC Action: {hvac_action}")
            print(f"  -> Heating Active: {hvac_action == 'heating'}")
            
            print(f"Method 2 - Mode + Temp: {hvac_mode}, {current_temp}°C -> {target_temp}°C")
            if current_temp and target_temp:
                temp_diff = float(target_temp) - float(current_temp)
                heating_needed = hvac_mode == 'heat' and temp_diff > 0.5
                print(f"  -> Temperature Difference: {temp_diff:.1f}°C")
                print(f"  -> Heating Needed: {heating_needed}")
            
            print(f"Method 3 - Entity State: {state}")
            print(f"  -> State-based Heating: {state == 'heat'}")
            
            # Recommended detection method
            print(f"\nRECOMMENDED DETECTION:")
            if hvac_action:
                print(f"✅ Use hvac_action: {hvac_action == 'heating'}")
            elif hvac_mode and current_temp and target_temp:
                heating = hvac_mode == 'heat' and float(target_temp) > float(current_temp) + 0.5
                print(f"⚠️  Use mode+temp fallback: {heating}")
            else:
                print(f"❌ Limited detection options available")
                
        else:
            print(f"Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.RequestException as e:
        print(f"Connection error: {e}")
        print("Make sure Home Assistant is running and accessible")
    except Exception as e:
        print(f"Error: {e}")

def test_heating_binary_sensor():
    """Test our heating detection binary sensor"""
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{HA_URL}/api/states/binary_sensor.zone_one_heating_active", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("\n" + "=" * 60)
            print("HEATING DETECTION BINARY SENSOR")
            print("=" * 60)
            print(f"State: {data.get('state')}")
            print(f"Attributes: {json.dumps(data.get('attributes', {}), indent=2)}")
        else:
            print(f"\n❌ Heating binary sensor not found (HTTP {response.status_code})")
            print("The heating detection sensor may not be configured yet")
            
    except Exception as e:
        print(f"Error checking binary sensor: {e}")

def check_pyephember2_changes():
    """Check for common PyEphEmber2 changes"""
    print("\n" + "=" * 60)
    print("PYEPHEMBER2 CHANGE CHECKLIST")
    print("=" * 60)
    
    checklist = [
        "1. Check if hvac_action attribute is still 'heating' when active",
        "2. Verify current_temperature and temperature attributes exist",
        "3. Confirm hvac_mode values (heat/off/auto)",
        "4. Check if entity state changes (heat/off/idle)",
        "5. Look for new attributes added in PyEphEmber2",
        "6. Verify supported_features hasn't changed",
        "7. Check if device_class or unit_of_measurement changed"
    ]
    
    for item in checklist:
        print(f"☐ {item}")

if __name__ == "__main__":
    print("PyEphEmber2 Home Assistant Integration Tester")
    print(f"Started at: {datetime.now()}")
    
    if HA_TOKEN == "your_ha_token_here":
        print("\n❌ ERROR: Please update HA_TOKEN in this script")
        print("1. Go to Home Assistant > Profile > Long-Lived Access Tokens")
        print("2. Create a new token")
        print("3. Update HA_TOKEN in this script")
        exit(1)
    
    test_climate_entity()
    test_heating_binary_sensor()
    check_pyephember2_changes()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. Review the attribute analysis above")
    print("2. Update heating detection if needed")
    print("3. Test the heating analytics dashboard")
    print("4. Check InfluxDB data storage")
    print("5. Verify mobile dashboard works correctly")