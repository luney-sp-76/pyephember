#!/usr/bin/env python3
"""
Check what climate and sensor entities exist in Home Assistant
Run this via SSH to your Home Assistant
"""

import requests
import json
import os

def check_ha_entities():
    """Check what entities exist in Home Assistant"""
    
    # You'll need to get a long-lived access token from HA
    token = os.environ.get('HA_TOKEN')
    ha_url = "http://localhost:8123"
    
    if not token:
        print("❌ Please set HA_TOKEN environment variable")
        print("Get token from: Profile → Long-Lived Access Tokens")
        return
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        # Get all states
        response = requests.get(f"{ha_url}/api/states", headers=headers)
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return
            
        entities = response.json()
        
        # Filter climate entities
        climate_entities = [e for e in entities if e['entity_id'].startswith('climate.')]
        sensor_entities = [e for e in entities if e['entity_id'].startswith('sensor.')]
        binary_entities = [e for e in entities if e['entity_id'].startswith('binary_sensor.')]
        
        print("🔥 CLIMATE ENTITIES FOUND:")
        print("=" * 40)
        for entity in climate_entities:
            name = entity['entity_id']
            state = entity['state']
            friendly_name = entity.get('attributes', {}).get('friendly_name', 'N/A')
            print(f"✅ {name}")
            print(f"   Name: {friendly_name}")
            print(f"   State: {state}")
            print()
        
        print(f"📊 SUMMARY:")
        print(f"   Climate entities: {len(climate_entities)}")
        print(f"   Sensor entities: {len(sensor_entities)}")
        print(f"   Binary sensors: {len(binary_entities)}")
        
        # Check for EPH-related entities
        eph_entities = [e for e in entities if 'eph' in e['entity_id'].lower()]
        if eph_entities:
            print(f"\n🔥 EPH-RELATED ENTITIES:")
            for entity in eph_entities:
                print(f"   • {entity['entity_id']}")
        
        return climate_entities
        
    except Exception as e:
        print(f"❌ Error checking entities: {e}")
        return []

def check_without_token():
    """Alternative method without API token"""
    print("🔍 Checking entity files...")
    
    # Check for entity registry
    registry_files = [
        "/config/.storage/core.entity_registry",
        "/config/.storage/core.device_registry"
    ]
    
    for file_path in registry_files:
        if os.path.exists(file_path):
            print(f"✅ Found: {file_path}")
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    entities = data.get('data', {}).get('entities', [])
                    climate_count = len([e for e in entities if e.get('entity_id', '').startswith('climate.')])
                    print(f"   Climate entities in registry: {climate_count}")
            except Exception as e:
                print(f"   Error reading file: {e}")
        else:
            print(f"⚠️  Not found: {file_path}")

if __name__ == "__main__":
    print("🧪 Home Assistant Entity Checker")
    print("=" * 40)
    
    # Try API method first
    entities = check_ha_entities()
    
    if not entities:
        print("\n🔧 Trying alternative method...")
        check_without_token()
        
    print(f"\n💡 To use the heating tracker:")
    print("1. Note your actual climate entity names above")
    print("2. Replace 'climate.living_room' etc. in the YAML files")
    print("3. Add the YAML to your configuration")
    print("4. Restart Home Assistant")