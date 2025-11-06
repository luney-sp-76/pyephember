#!/usr/bin/env python3
"""
Simple EPH Zone Diagnostic - Prompt for credentials
"""

import os
import json
import getpass
from pyephember2.pyephember2 import EphEmber

# Try environment variables first, then prompt
username = os.getenv('EPH_USERNAME')
password = os.getenv('EPH_PASSWORD')

if not username or not password:
    print("EPH credentials not found in environment variables.")
    print("Please enter your EPH Controls credentials:")
    username = input("Username: ").strip()
    password = getpass.getpass("Password: ").strip()

if username and password:
    try:
        print("=== Simple EPH Zone Diagnostic ===")
        print(f"Connecting as user: {username}")
        
        eph = EphEmber(username, password)
        print("✓ Connection established")
        
        # 1. Check zone names
        print("\n1. Getting zone names...")
        try:
            zone_names = eph.get_zone_names()
            print(f"Zone names: {zone_names}")
        except Exception as e:
            print(f"get_zone_names() error: {e}")
        
        # 2. Check homes structure
        print("\n2. Examining homes...")
        try:
            homes = eph.get_homes()
            print(f"Homes: {type(homes)} with {len(homes) if hasattr(homes, '__len__') else 'unknown'} items")
            
            if isinstance(homes, list) and len(homes) > 0:
                home = homes[0]
                if isinstance(home, dict):
                    print(f"Home keys: {list(home.keys())}")
                    
                    # Look specifically for zone data
                    if 'zones' in home:
                        zones_data = home['zones']
                        print(f"Found 'zones' key: {type(zones_data)}")
                        if isinstance(zones_data, list):
                            print(f"Zones list has {len(zones_data)} items")
                            for i, zone in enumerate(zones_data[:3]):
                                if isinstance(zone, dict):
                                    print(f"  Zone {i}: {list(zone.keys())}")
                                    zone_id = zone.get('id') or zone.get('name')
                                    if zone_id:
                                        print(f"    Zone ID: {zone_id}")
                                        # Try temperature access
                                        try:
                                            temp = eph.get_zone_temperature(zone_id)
                                            print(f"    ✓ Temperature: {temp}")
                                        except Exception as e:
                                            print(f"    ✗ Temperature error: {e}")
                    
                    # Look for other potential zone containers
                    for key, value in home.items():
                        if 'zone' in key.lower() and key != 'zones':
                            print(f"Found zone-related key '{key}': {type(value)}")
                    
        except Exception as e:
            print(f"Homes error: {e}")
        
        # 3. Try numeric zone IDs
        print("\n3. Testing numeric zone IDs...")
        for i in range(3):
            try:
                temp = eph.get_zone_temperature(str(i))
                print(f"Zone '{i}': {temp}°")
            except Exception as e:
                print(f"Zone '{i}': {e}")
        
        # 4. Try Home Assistant entity-style IDs
        print("\n4. Testing HA-style zone IDs...")
        test_ids = ['castle', 'Castle', 'CASTLE', 'turtle_castle', 'TurtleCastle']
        for zone_id in test_ids:
            try:
                temp = eph.get_zone_temperature(zone_id)
                print(f"Zone '{zone_id}': {temp}°")
            except Exception as e:
                print(f"Zone '{zone_id}': {e}")
                
    except Exception as e:
        print(f"Main error: {e}")
else:
    print("No credentials provided")