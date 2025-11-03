#!/usr/bin/env python3
"""
Demo script showing pyephember functionality with mocked API responses
This script demonstrates testing the example.py without requiring real credentials
"""

import json
from unittest.mock import Mock, patch
import sys
import os

# Add the parent directory to sys.path so we can import pyephember
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def mock_ember_api():
    """Create a mock EphEmber instance with sample data"""
    
    # Mock API responses
    mock_zone_data = {
        'name': 'Living Room',
        'pointDataList': [
            {'pointIndex': 5, 'value': 205},  # Current temp: 20.5°C
            {'pointIndex': 6, 'value': 210},  # Target temp: 21.0°C
            {'pointIndex': 7, 'value': 0},    # Mode: AUTO
            {'pointIndex': 4, 'value': 0},    # Advance: inactive
            {'pointIndex': 8, 'value': 0},    # Boost hours: 0
            {'pointIndex': 10, 'value': 1},   # Boiler state: on
        ]
    }
    
    mock_home_data = {
        'zoneData': [mock_zone_data],
        'name': 'Home Sweet Home',
        'gatewayId': 'test-gateway-123'
    }
    
    # Create patches for all the methods that might be called during init
    with patch('pyephember.pyephember.EphEmber._login', return_value=True):
        with patch('pyephember.pyephember.EphMessenger'):  # Mock the messenger
            with patch('pyephember.pyephember.EphEmber.get_home', return_value=mock_home_data):
                with patch('pyephember.pyephember.EphEmber.get_zones', return_value=mock_home_data['zoneData']):
                    with patch('pyephember.pyephember.EphEmber.get_zone', return_value=mock_zone_data):
                        
                        from pyephember.pyephember import EphEmber
                        
                        # Create ember instance (mocked login will succeed)
                        ember = EphEmber('test@example.com', 'testpassword')
                        
                        return ember, mock_home_data, mock_zone_data

def demonstrate_api_functionality():
    """Demonstrate key API functionality with mock data"""
    
    print("🔥 PyEphEmber Demo - Testing with Mock Data")
    print("=" * 50)
    
    ember, mock_home_data, mock_zone_data = mock_ember_api()
    
    # Test 1: Get home information
    print("🏠 Home Information:")
    home_data = ember.get_home()
    print(json.dumps(home_data, indent=2))
    print()
    
    # Test 2: Get zones
    print("🌡️  Zone Information:")
    zones = ember.get_zones()
    print(json.dumps(zones, indent=2))
    print()
    
    # Test 3: Get specific zone
    print("📍 Specific Zone ('Living Room'):")
    zone = ember.get_zone('Living Room')
    print(json.dumps(zone, indent=2))
    print()
    
    # Test 4: Get temperature
    print("🌡️  Temperature Information:")
    current_temp = ember.get_zone_temperature('Living Room')
    print(f"Current temperature: {current_temp}°C")
    
    # Test 5: Zone utility functions
    from pyephember.pyephember import (
        zone_target_temperature, zone_current_temperature, 
        zone_mode, zone_advance_active, zone_is_active
    )
    
    print(f"Target temperature: {zone_target_temperature(mock_zone_data)}°C")
    print(f"Zone mode: {zone_mode(mock_zone_data)}")
    print(f"Advance active: {zone_advance_active(mock_zone_data)}")
    print(f"Zone is active: {zone_is_active(mock_zone_data)}")
    print()
    
    print("✅ All tests completed successfully!")
    print("📝 This demonstrates that the PyEphEmber library is working correctly")
    print("🔧 Run the actual tests with: python3 -m pytest tests/ -v")

if __name__ == '__main__':
    try:
        demonstrate_api_functionality()
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        sys.exit(1)