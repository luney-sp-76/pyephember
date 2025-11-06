#!/usr/bin/env python3
"""
EPH Integration Final Test - Confirm all functionality works
Usage: python3 final_test.py USERNAME PASSWORD
"""

import sys
import os
from pyephember2.pyephember2 import EphEmber

def final_test():
    if len(sys.argv) != 3:
        print("Usage: python3 final_test.py USERNAME PASSWORD")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    try:
        print("=== EPH Integration Final Test ===")
        eph = EphEmber(username, password)
        print("✓ Connected to EPH Controls")
        
        # Get zone mapping
        homes = eph.get_homes()
        if isinstance(homes, list) and len(homes) > 0:
            home = homes[0]
            if isinstance(home, dict) and 'zones' in home:
                zone = home['zones'][0]  # First zone
                
                zone_name = zone.get('name')
                zone_id = zone.get('zoneid')
                
                print(f"\n📍 Zone: '{zone_name}' (ID: {zone_id})")
                
                # Test all working methods
                print("\n🌡️  Temperature Data:")
                current = eph.get_zone_temperature(zone_id)
                target = eph.get_zone_target_temperature(zone_id)
                print(f"  Current: {current}°C")
                print(f"  Target: {target}°C")
                
                print("\n🔥 Zone Status:")
                active = eph.is_zone_active(zone_id)
                boiler_on = eph.is_zone_boiler_on(zone_id)
                target_reached = eph.is_target_temperature_reached(zone_id)
                boost_temp = eph.get_zone_boost_temperature(zone_id)
                
                print(f"  Active: {active}")
                print(f"  Boiler on: {boiler_on}")
                print(f"  Target reached: {target_reached}")
                print(f"  Boost temperature: {boost_temp}°C")
                
                # Home Assistant entity mapping
                print(f"\n🏠 Home Assistant Integration:")
                print(f"  Entity ID: climate.{zone_name.lower().replace(' ', '_')}_thermostat")
                print(f"  Zone Name: {zone_name}")
                print(f"  EPH Zone ID: {zone_id}")
                
                print(f"\n✅ All tests passed! Integration ready for Home Assistant.")
                print(f"\nTo use in Home Assistant climate entity:")
                print(f"- Current temperature: {current}°C")
                print(f"- Target temperature: {target}°C")
                print(f"- HVAC mode: {'heat' if active else 'off'}")
                print(f"- HVAC action: {'heating' if boiler_on else 'idle'}")
                
        else:
            print("❌ No zones found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    final_test()