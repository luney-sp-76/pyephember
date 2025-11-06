#!/usr/bin/env python3
"""
EPH Zone Discovery Script - Find the correct zone identifiers
"""

import os
from pyephember2.pyephember2 import EphEmber

username = os.getenv('EPH_USERNAME')
password = os.getenv('EPH_PASSWORD')

if username and password:
    try:
        eph = EphEmber(username, password)
        print("=== EPH Zone Discovery ===")
        
        # Try get_zones() method
        print("\n1. Testing get_zones()...")
        try:
            zones = eph.get_zones()
            print(f"get_zones() result: {zones}")
            print(f"Type: {type(zones)}")
            if hasattr(zones, '__dict__'):
                print(f"Attributes: {list(zones.__dict__.keys())}")
        except Exception as e:
            print(f"get_zones() error: {e}")
        
        # Try get_zone_names()
        print("\n2. Testing get_zone_names()...")
        try:
            zone_names = eph.get_zone_names()
            print(f"get_zone_names() result: {zone_names}")
        except Exception as e:
            print(f"get_zone_names() error: {e}")
        
        # Try different zone identifiers
        test_zones = ["ONE", "Turtle Castle", "1", "0", "Castle", "turtle_castle"]
        
        print("\n3. Testing different zone identifiers...")
        for test_zone in test_zones:
            print(f"\nTesting zone identifier: '{test_zone}'")
            
            # Test temperature
            try:
                temp = eph.get_zone_temperature(test_zone)
                print(f"  ✓ Temperature: {temp}°C")
            except Exception as e:
                print(f"  ✗ Temperature: {e}")
            
            # Test target temperature
            try:
                target = eph.get_zone_target_temperature(test_zone)
                print(f"  ✓ Target: {target}°C")
            except Exception as e:
                print(f"  ✗ Target: {e}")
            
            # Test zone info
            try:
                zone_info = eph.get_zone(test_zone)
                print(f"  ✓ Zone info: {type(zone_info)}")
                if hasattr(zone_info, '__dict__'):
                    print(f"    Attributes: {list(zone_info.__dict__.keys())}")
            except Exception as e:
                print(f"  ✗ Zone info: {e}")
        
        # Try to get home details
        print("\n4. Testing get_home_details()...")
        try:
            home_details = eph.get_home_details()
            print(f"Home details: {home_details}")
            print(f"Type: {type(home_details)}")
        except Exception as e:
            print(f"get_home_details() error: {e}")
        
        # Try to get homes
        print("\n5. Testing get_homes()...")
        try:
            homes = eph.get_homes()
            print(f"Homes: {homes}")
            print(f"Type: {type(homes)}")
        except Exception as e:
            print(f"get_homes() error: {e}")
            
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No credentials found")