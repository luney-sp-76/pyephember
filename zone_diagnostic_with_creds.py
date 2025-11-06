#!/usr/bin/env python3
"""
EPH Zone Diagnostic with credential parameters
Usage: python3 zone_diagnostic_with_creds.py USERNAME PASSWORD
"""

import sys
import os
from pyephember2.pyephember2 import EphEmber

def main():
    # Get credentials from command line args or environment
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
        print(f"Using credentials from command line for user: {username}")
    else:
        username = os.getenv('EPH_USERNAME')
        password = os.getenv('EPH_PASSWORD')
        if username and password:
            print(f"Using credentials from environment for user: {username}")
        else:
            print("Usage: python3 zone_diagnostic_with_creds.py USERNAME PASSWORD")
            print("Or set EPH_USERNAME and EPH_PASSWORD environment variables")
            sys.exit(1)

    try:
        print("=== EPH Zone Diagnostic ===")
        eph = EphEmber(username, password)
        print("✓ Connected to EPH Controls")
        
        # 1. Get zone names
        print("\n1. Zone names:")
        try:
            zone_names = eph.get_zone_names()
            print(f"  Found zones: {zone_names}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # 2. Check homes structure
        print("\n2. Home structure:")
        try:
            homes = eph.get_homes()
            if isinstance(homes, list) and len(homes) > 0:
                home = homes[0]
                print(f"  Home type: {type(home)}")
                if isinstance(home, dict):
                    print(f"  Home keys: {list(home.keys())}")
                    
                    # Look for zone data in home
                    for key, value in home.items():
                        if 'zone' in key.lower():
                            print(f"  Found zone key '{key}': {type(value)}")
                            if isinstance(value, list) and len(value) > 0:
                                print(f"    List with {len(value)} items")
                                first_item = value[0]
                                if isinstance(first_item, dict):
                                    print(f"    First item keys: {list(first_item.keys())}")
        except Exception as e:
            print(f"  Error: {e}")
        
        # 3. Test temperature access methods
        print("\n3. Testing temperature access:")
        test_zone_ids = ['Turtle Castle', 'ONE', '0', '1', 'castle', 'Castle']
        
        for zone_id in test_zone_ids:
            try:
                temp = eph.get_zone_temperature(zone_id)
                print(f"  ✓ Zone '{zone_id}': {temp}°C")
                break  # Found working zone ID!
            except Exception as e:
                print(f"  ✗ Zone '{zone_id}': {e}")
        
        # 4. Check zones object structure
        print("\n4. Zones object analysis:")
        try:
            zones_obj = eph.get_zones()
            print(f"  Type: {type(zones_obj)}")
            if isinstance(zones_obj, dict):
                non_circular_keys = [k for k in zones_obj.keys() if k not in ['Prev', 'Next'] and not str(k).isdigit()]
                print(f"  Non-circular keys: {non_circular_keys}")
                
                # Look for zone-related data
                for key in non_circular_keys[:5]:  # Limit to first 5 keys
                    value = zones_obj[key]
                    print(f"    {key}: {type(value)}")
                    if isinstance(value, (str, int, float, bool)):
                        print(f"      Value: {value}")
                    elif isinstance(value, list) and len(value) < 10:
                        print(f"      Content: {value}")
                        
        except Exception as e:
            print(f"  Error: {e}")
            
    except Exception as e:
        print(f"Main error: {e}")

if __name__ == "__main__":
    main()