#!/usr/bin/env python3
"""
Simple EPH connection test script
"""

import os
import sys
from pyephember2.pyephember2 import EphEmber

def test_eph_connection():
    """Test EPH connection with credentials"""
    
    # Check for credentials
    username = os.getenv('EPH_USERNAME')
    password = os.getenv('EPH_PASSWORD')
    
    if not username or not password:
        print("ERROR: EPH_USERNAME and EPH_PASSWORD environment variables must be set")
        print("Usage:")
        print("  export EPH_USERNAME='your_username'")
        print("  export EPH_PASSWORD='your_password'")
        print("  python3 test_eph_connection.py")
        return False
    
    try:
        print("Testing EPH connection...")
        eph = EphEmber(username, password)
        
        print("✓ EphEmber instance created successfully")
        
        # Test basic functionality
        print("Testing get_zone_names()...")
        zone_names = eph.get_zone_names()
        print(f"✓ Found zones: {zone_names}")
        
        # Test temperature reading for each zone
        for zone_name in zone_names:
            print(f"Testing temperature for zone '{zone_name}'...")
            try:
                temp = eph.get_zone_temperature(zone_name)
                print(f"✓ Current temperature: {temp}°C")
            except Exception as e:
                print(f"✗ Temperature read failed: {e}")
            
            try:
                target = eph.get_zone_target_temperature(zone_name)
                print(f"✓ Target temperature: {target}°C")
            except Exception as e:
                print(f"✗ Target temperature read failed: {e}")
            
            # Test other zone methods
            try:
                zone_info = eph.get_zone(zone_name)
                print(f"✓ Zone info retrieved: {type(zone_info)}")
            except Exception as e:
                print(f"✗ Zone info failed: {e}")
            
            try:
                is_active = eph.is_zone_active(zone_name)
                print(f"✓ Zone active status: {is_active}")
            except Exception as e:
                print(f"✗ Zone active status failed: {e}")
            
            break  # Test only first zone
        
        print("\n=== EPH Connection Test PASSED ===")
        return True
        
    except Exception as e:
        print(f"✗ EPH connection failed: {e}")
        print("\n=== EPH Connection Test FAILED ===")
        return False

if __name__ == "__main__":
    success = test_eph_connection()
    sys.exit(0 if success else 1)