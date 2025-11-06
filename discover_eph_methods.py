#!/usr/bin/env python3
"""
EPH API Method Discovery Script
Finds available methods in the EphEmber class
"""

import os
import sys
from pyephember2.pyephember2 import EphEmber

def discover_eph_methods():
    """Discover available methods in EphEmber class"""
    
    username = os.getenv('EPH_USERNAME')
    password = os.getenv('EPH_PASSWORD')
    
    if not username or not password:
        print("ERROR: EPH_USERNAME and EPH_PASSWORD environment variables must be set")
        return False
    
    try:
        print("Creating EphEmber instance...")
        eph = EphEmber(username, password)
        print("✓ EphEmber instance created successfully")
        
        print("\n=== Available Methods ===")
        methods = [method for method in dir(eph) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  {method}")
        
        print("\n=== Testing Key Methods ===")
        
        # Test methods that might exist
        test_methods = [
            'get_zones',
            'list_zones', 
            'zones',
            'get_temperature',
            'get_target_temperature',
            'set_zone_advance',
            'get_programs',
            'get_status'
        ]
        
        for method_name in test_methods:
            if hasattr(eph, method_name):
                print(f"✓ {method_name} - EXISTS")
                try:
                    method = getattr(eph, method_name)
                    if callable(method):
                        print(f"  └─ Callable: {method.__doc__ or 'No docstring'}")
                except Exception as e:
                    print(f"  └─ Error accessing: {e}")
            else:
                print(f"✗ {method_name} - NOT FOUND")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    success = discover_eph_methods()
    sys.exit(0 if success else 1)