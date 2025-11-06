#!/usr/bin/env python3
"""
Test Enhanced EPH Script with Correct Zone IDs
"""

import sys
import os
sys.path.append('/Users/paulolphert/Ember/pyephember')

# Test the enhanced script
from enhanced_eph_ember import EPHHomeAssistantIntegration

def test_enhanced_script():
    """Test the enhanced script with credentials"""
    
    # Get credentials from command line
    if len(sys.argv) != 3:
        print("Usage: python3 test_enhanced_fixed.py USERNAME PASSWORD")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    try:
        print("=== Testing Enhanced EPH Script ===")
        
        # Initialize integration
        integration = EPHHomeAssistantIntegration(username, password)
        print("✓ Integration initialized")
        
        # Test zone mapping
        print(f"\nZone mapping: {integration.zone_mapping}")
        
        # Test with the zone name we found
        zone_name = "ONE"  # This was the actual zone name from our discovery
        print(f"\nTesting zone '{zone_name}':")
        
        # Test temperature functions
        current_temp = integration.get_temperature(zone_name)
        print(f"Current temperature: {current_temp}°C")
        
        target_temp = integration.get_target_temperature(zone_name)
        print(f"Target temperature: {target_temp}°C")
        
        # Test zone status
        status = integration.get_zone_status(zone_name)
        print(f"\nZone status:")
        print(f"  Current: {status.get('current_temperature', 'N/A')}°C")
        print(f"  Target: {status.get('target_temperature', 'N/A')}°C")
        print(f"  Heating active: {status.get('heating_active', 'N/A')}")
        print(f"  Internal ID: {status.get('internal_id', 'N/A')}")
        
        print("\n✅ Enhanced script working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_script()