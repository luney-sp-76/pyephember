#!/usr/bin/env python3
"""
EPH Zone ID Discovery - Extract and test actual zone IDs
Usage: python3 zone_id_discovery.py USERNAME PASSWORD
"""

import sys
import os
from pyephember2.pyephember2 import EphEmber

def main():
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    else:
        print("Usage: python3 zone_id_discovery.py USERNAME PASSWORD")
        sys.exit(1)

    try:
        print("=== EPH Zone ID Discovery ===")
        eph = EphEmber(username, password)
        print("✓ Connected to EPH Controls")
        
        # Get homes and extract actual zone IDs
        homes = eph.get_homes()
        if isinstance(homes, list) and len(homes) > 0:
            home = homes[0]
            if isinstance(home, dict) and 'zones' in home:
                zones_list = home['zones']
                print(f"\nFound {len(zones_list)} zone(s) in home:")
                
                working_zone_ids = []
                
                for i, zone in enumerate(zones_list):
                    if isinstance(zone, dict):
                        print(f"\n--- Zone {i+1} Details ---")
                        print(f"Zone name: {zone.get('name', 'Unknown')}")
                        print(f"Zone ID (zoneid): {zone.get('zoneid', 'Not found')}")
                        print(f"UID: {zone.get('uid', 'Not found')}")
                        print(f"MAC: {zone.get('mac', 'Not found')}")
                        print(f"Online: {zone.get('isonline', 'Unknown')}")
                        
                        # Test all possible zone identifiers from this zone object
                        test_ids = [
                            zone.get('zoneid'),
                            zone.get('uid'), 
                            zone.get('mac'),
                            zone.get('name'),
                            str(i),  # Index
                            str(i+1), # 1-based index
                        ]
                        
                        print(f"\nTesting temperature access for zone '{zone.get('name')}':")
                        
                        for test_id in test_ids:
                            if test_id is not None:
                                try:
                                    temp = eph.get_zone_temperature(str(test_id))
                                    print(f"  ✅ SUCCESS! ID '{test_id}': {temp}°C")
                                    working_zone_ids.append(str(test_id))
                                    
                                    # Also test target temperature
                                    try:
                                        target_temp = eph.get_zone_target_temperature(str(test_id))
                                        print(f"  ✅ Target temp for '{test_id}': {target_temp}°C")
                                    except Exception as e2:
                                        print(f"  ⚠️  Target temp error for '{test_id}': {e2}")
                                        
                                except Exception as e:
                                    print(f"  ❌ ID '{test_id}': {e}")
                
                if working_zone_ids:
                    print(f"\n🎉 FOUND WORKING ZONE IDs: {working_zone_ids}")
                    
                    # Test other methods with working ID
                    working_id = working_zone_ids[0]
                    print(f"\nTesting additional methods with working ID '{working_id}':")
                    
                    test_methods = [
                        ('get_zone_mode', lambda: eph.get_zone_mode(working_id)),
                        ('is_zone_active', lambda: eph.is_zone_active(working_id)),
                        ('is_zone_boiler_on', lambda: eph.is_zone_boiler_on(working_id)),
                        ('is_target_temperature_reached', lambda: eph.is_target_temperature_reached(working_id)),
                        ('get_zone_boost_temperature', lambda: eph.get_zone_boost_temperature(working_id)),
                    ]
                    
                    for method_name, method_call in test_methods:
                        try:
                            result = method_call()
                            print(f"  ✅ {method_name}: {result}")
                        except Exception as e:
                            print(f"  ❌ {method_name}: {e}")
                            
                else:
                    print("\n❌ No working zone IDs found!")
                    
        else:
            print("❌ No homes found or invalid home structure")
            
    except Exception as e:
        print(f"❌ Main error: {e}")

if __name__ == "__main__":
    main()