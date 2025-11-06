#!/usr/bin/env python3
"""
Interactive EPH connection test script
"""

import sys
import getpass
from pyephember2.pyephember2 import EphEmber

def test_eph_connection_interactive():
    """Test EPH connection with interactive credential input"""
    
    print("=== EPH Connection Test ===")
    print()
    
    # Get credentials interactively
    username = input("Enter EPH username (polphert@gmail.com): ").strip()
    if not username:
        username = "polphert@gmail.com"
    
    password = getpass.getpass("Enter EPH password: ")
    
    if not password:
        print("ERROR: Password is required")
        return False
    
    try:
        print("\nTesting EPH connection...")
        eph = EphEmber(username, password)
        print("✓ EphEmber instance created successfully")
        
        # Test basic functionality
        print("Testing get_zone_names()...")
        zone_names = eph.get_zone_names()
        print(f"✓ Found zones: {zone_names}")
        
        # Test temperature reading for the first zone
        if zone_names:
            zone_name = zone_names[0]
            print(f"\nTesting zone '{zone_name}':")
            
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
            
            try:
                zone_info = eph.get_zone(zone_name)
                print(f"✓ Zone info retrieved successfully")
                print(f"  Zone data type: {type(zone_info)}")
                if hasattr(zone_info, '__dict__'):
                    print(f"  Zone attributes: {list(zone_info.__dict__.keys())}")
            except Exception as e:
                print(f"✗ Zone info failed: {e}")
            
            try:
                is_active = eph.is_zone_active(zone_name)
                print(f"✓ Zone active status: {is_active}")
            except Exception as e:
                print(f"✗ Zone active status failed: {e}")
            
            try:
                is_boiler_on = eph.is_zone_boiler_on(zone_name)
                print(f"✓ Zone boiler status: {is_boiler_on}")
            except Exception as e:
                print(f"✗ Zone boiler status failed: {e}")
        
        print("\n=== EPH Connection Test PASSED ===")
        print(f"Your EPH system is accessible with username: {username}")
        print(f"Zone names to use in scripts: {zone_names}")
        
        return True, username, password, zone_names
        
    except Exception as e:
        print(f"\n✗ EPH connection failed: {e}")
        print("\n=== EPH Connection Test FAILED ===")
        return False, None, None, None

def create_env_setup_script(username, password):
    """Create a script to set up environment variables"""
    env_script = f"""#!/bin/bash
# EPH Environment Setup Script
# Source this file to set up your EPH credentials

export EPH_USERNAME='{username}'
export EPH_PASSWORD='{password}'

echo "EPH credentials set:"
echo "  Username: $EPH_USERNAME"
echo "  Password: [hidden]"
echo ""
echo "You can now run:"
echo "  python3 enhanced_eph_ember.py status"
echo "  python3 enhanced_eph_ember.py temperature"
"""
    
    with open('eph_env_setup.sh', 'w') as f:
        f.write(env_script)
    
    print(f"\n✓ Created eph_env_setup.sh")
    print("To use your EPH integration:")
    print("  source eph_env_setup.sh")
    print("  python3 enhanced_eph_ember.py status")

if __name__ == "__main__":
    success, username, password, zones = test_eph_connection_interactive()
    
    if success:
        create_env_setup_script(username, password)
        print(f"\n🎉 EPH integration is ready!")
        print(f"Available zones: {', '.join(zones)}")
    
    sys.exit(0 if success else 1)