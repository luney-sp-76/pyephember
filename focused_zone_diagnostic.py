#!/usr/bin/env python3
"""
Focused EPH Zone Diagnostic - Skip circular data, focus on zone access
"""

import os
import json
from pyephember2.pyephember2 import EphEmber

username = os.getenv('EPH_USERNAME')
password = os.getenv('EPH_PASSWORD')

def safe_dict_extract(obj, max_depth=2, current_depth=0):
    """Safely extract dictionary info without circular references"""
    if current_depth >= max_depth:
        return f"<Depth limit {max_depth} reached>"
    
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in obj.__dict__.items():
            if key in ['Prev', 'Next', 'Count']:  # Skip circular reference keys
                result[key] = f"<Circular reference: {type(value)}>"
            elif isinstance(value, (str, int, float, bool, type(None))):
                result[key] = value
            elif hasattr(value, '__dict__'):
                result[key] = safe_dict_extract(value, max_depth, current_depth + 1)
            else:
                result[key] = f"<{type(value).__name__}>"
        return result
    else:
        return str(obj)

if username and password:
    try:
        eph = EphEmber(username, password)
        print("=== Focused EPH Zone Diagnostic ===")
        
        # 1. Check zone names first
        print("\n1. Getting zone names...")
        try:
            zone_names = eph.get_zone_names()
            print(f"Zone names: {zone_names}")
        except Exception as e:
            print(f"get_zone_names() error: {e}")
        
        # 2. Examine homes structure carefully
        print("\n2. Examining homes structure...")
        try:
            homes = eph.get_homes()
            print(f"Homes type: {type(homes)}")
            print(f"Number of homes: {len(homes) if hasattr(homes, '__len__') else 'Unknown'}")
            
            if isinstance(homes, list) and len(homes) > 0:
                first_home = homes[0]
                print(f"\nFirst home type: {type(first_home)}")
                if isinstance(first_home, dict):
                    print("First home keys:", list(first_home.keys()))
                    # Look for zone-related keys
                    for key, value in first_home.items():
                        if 'zone' in key.lower() or key in ['zones', 'Zones', 'ZONES']:
                            print(f"  {key}: {type(value)} - {value if not hasattr(value, '__len__') or len(str(value)) < 100 else f'{type(value)} with {len(value)} items'}")
                        elif key in ['name', 'Name', 'id', 'Id', 'ID']:
                            print(f"  {key}: {value}")
                            
        except Exception as e:
            print(f"get_homes() error: {e}")
        
        # 3. Try direct zone access with indices
        print("\n3. Trying zone access with numeric indices...")
        for i in range(5):  # Try indices 0-4
            try:
                zone_temp = eph.get_zone_temperature(str(i))
                print(f"get_zone_temperature('{i}'): {zone_temp}")
            except Exception as e:
                print(f"get_zone_temperature('{i}') error: {e}")
        
        # 4. Try to find zones through homes
        print("\n4. Looking for zones through homes...")
        try:
            homes = eph.get_homes()
            if isinstance(homes, list) and len(homes) > 0:
                home = homes[0]
                if isinstance(home, dict):
                    # Look for any zone-related data in the home
                    for key, value in home.items():
                        if isinstance(value, list) and len(value) > 0:
                            first_item = value[0]
                            if isinstance(first_item, dict) and any(k.lower().find('zone') >= 0 or k.lower().find('temp') >= 0 for k in first_item.keys()):
                                print(f"Found potential zone data in home['{key}']:")
                                print(f"  Type: {type(value)}, Length: {len(value)}")
                                print(f"  First item keys: {list(first_item.keys()) if isinstance(first_item, dict) else type(first_item)}")
                                
                                # Try to extract zone identifiers
                                for item in value[:3]:  # Check first 3 items
                                    if isinstance(item, dict):
                                        zone_id = item.get('id') or item.get('zoneId') or item.get('zone_id') or item.get('name')
                                        if zone_id:
                                            print(f"    Potential zone ID: {zone_id}")
                                            # Try this ID
                                            try:
                                                temp = eph.get_zone_temperature(zone_id)
                                                print(f"    SUCCESS! get_zone_temperature('{zone_id}'): {temp}")
                                            except Exception as e:
                                                print(f"    get_zone_temperature('{zone_id}') error: {e}")
                                break
        except Exception as e:
            print(f"Error examining homes for zones: {e}")
        
        # 5. Check the raw zones object without circular reference issues
        print("\n5. Examining zones object structure...")
        try:
            zones_obj = eph.get_zones()
            print(f"zones_obj type: {type(zones_obj)}")
            
            if isinstance(zones_obj, dict):
                print("Zone object top-level keys:", list(zones_obj.keys()))
                for key, value in zones_obj.items():
                    if key not in ['Prev', 'Next'] and not str(key).isdigit():  # Skip circular refs and program data
                        print(f"  {key}: {type(value)}")
                        if isinstance(value, dict) and len(value) < 10:  # Small dicts only
                            print(f"    Content: {value}")
                        elif isinstance(value, list) and len(value) < 5:  # Small lists only
                            print(f"    Content: {value}")
                            
        except Exception as e:
            print(f"get_zones() examination error: {e}")
            
    except Exception as e:
        print(f"Main error: {e}")
else:
    print("No credentials found")