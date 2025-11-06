#!/usr/bin/env python3
"""
EPH Zone Access Diagnostic - Focus on finding working zone access
"""

import os
from pyephember2.pyephember2 import EphEmber

username = os.getenv('EPH_USERNAME')
password = os.getenv('EPH_PASSWORD')

if username and password:
    try:
        eph = EphEmber(username, password)
        print("=== EPH Zone Access Diagnostic ===")
        
        # Let's try to get the actual zone objects and examine their structure
        print("\n1. Examining get_zones() return object...")
        try:
            zones_obj = eph.get_zones()
            print(f"get_zones() type: {type(zones_obj)}")
            
            if hasattr(zones_obj, '__dict__'):
                print("Zone object attributes:")
                for attr in zones_obj.__dict__.keys():
                    print(f"  {attr}: {type(getattr(zones_obj, attr))}")
                    
            if hasattr(zones_obj, '__iter__'):
                print("Zone object is iterable, examining items...")
                for i, item in enumerate(zones_obj):
                    print(f"  Item {i}: {type(item)} - {item}")
                    if hasattr(item, '__dict__'):
                        print(f"    Attributes: {list(item.__dict__.keys())}")
                    if i > 2:  # Limit to first 3 items
                        break
                        
        except Exception as e:
            print(f"get_zones() error: {e}")
        
        # Try to examine what get_zone returns for different inputs
        print("\n2. Examining get_zone() with different identifiers...")
        test_ids = ["Turtle Castle", "ONE", "0", "1"]
        
        for zone_id in test_ids:
            try:
                zone_obj = eph.get_zone(zone_id)
                print(f"\nget_zone('{zone_id}'):")
                print(f"  Type: {type(zone_obj)}")
                if hasattr(zone_obj, '__dict__'):
                    attrs = zone_obj.__dict__
                    print(f"  Attributes: {list(attrs.keys())}")
                    # Show some key attributes
                    for key in ['name', 'id', 'zone_id', 'temperature', 'target']:
                        if key in attrs:
                            print(f"    {key}: {attrs[key]}")
                elif hasattr(zone_obj, '__str__'):
                    print(f"  String repr: {str(zone_obj)}")
                    
            except Exception as e:
                print(f"get_zone('{zone_id}') error: {e}")
        
        # Try home-related methods to see if zones are nested under homes
        print("\n3. Examining home structure...")
        try:
            homes = eph.get_homes()
            print(f"get_homes() type: {type(homes)}")
            if hasattr(homes, '__iter__'):
                for i, home in enumerate(homes):
                    print(f"  Home {i}: {type(home)}")
                    if hasattr(home, '__dict__'):
                        print(f"    Attributes: {list(home.__dict__.keys())}")
                    if i > 1:  # Limit to first 2 homes
                        break
        except Exception as e:
            print(f"get_homes() error: {e}")
        
        print("\n4. Looking for alternative temperature access methods...")
        # Check all methods that might give us temperature access
        methods = [attr for attr in dir(eph) if 'temp' in attr.lower() or 'zone' in attr.lower()]
        print(f"Methods containing 'temp' or 'zone': {methods}")
        
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No credentials found")