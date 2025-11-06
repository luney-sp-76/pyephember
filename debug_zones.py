#!/usr/bin/env python3
"""
Simple EPH zone name test
"""

import os
from pyephember2.pyephember2 import EphEmber

username = os.getenv('EPH_USERNAME')
password = os.getenv('EPH_PASSWORD')

if username and password:
    try:
        eph = EphEmber(username, password)
        zone_names = eph.get_zone_names()
        print(f"Zone names from API: {zone_names}")
        print(f"Zone names type: {type(zone_names)}")
        
        if zone_names:
            first_zone = zone_names[0]
            print(f"Testing first zone: '{first_zone}'")
            
            try:
                temp = eph.get_zone_temperature(first_zone)
                print(f"Temperature: {temp}")
            except Exception as e:
                print(f"Temperature error: {e}")
                
            try:
                target = eph.get_zone_target_temperature(first_zone)
                print(f"Target temperature: {target}")
            except Exception as e:
                print(f"Target temperature error: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No credentials found")