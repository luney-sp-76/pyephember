#!/usr/bin/env python3
"""
Zone Discovery Script - Shows all zones in your EPH Ember system
"""
import sys
import json

def discover_zones():
    """Discover and display all zones in the system"""
    
    # You'll need to set these with your credentials
    email = input("Enter your EPH Ember email: ")
    password = input("Enter your EPH Ember password: ")
    
    try:
        from pyephember.pyephember import EphEmber
        
        print("\n🔐 Connecting to EPH Ember...")
        ember = EphEmber(email, password)
        
        print("✅ Connected successfully!")
        print("\n🏠 Discovering zones...")
        
        # Get all zones
        zones = ember.get_zones()
        zone_names = ember.get_zone_names()
        
        print(f"\n📍 Found {len(zone_names)} zones:")
        for i, name in enumerate(zone_names, 1):
            print(f"  {i}. {name}")
        
        print(f"\n📊 Detailed Zone Information:")
        print("=" * 50)
        
        for zone_name in zone_names:
            try:
                zone = ember.get_zone(zone_name)
                current_temp = ember.get_zone_temperature(zone_name)
                target_temp = ember.get_zone_target_temperature(zone_name)
                is_active = ember.is_zone_active(zone_name)
                
                print(f"\n🌡️  Zone: {zone_name}")
                print(f"   Current Temperature: {current_temp}°C")
                print(f"   Target Temperature:  {target_temp}°C")
                print(f"   Zone Active: {'Yes' if is_active else 'No'}")
                
            except Exception as e:
                print(f"   ❌ Error reading zone {zone_name}: {e}")
        
        print(f"\n💡 To control these zones programmatically:")
        print(f"   ember.set_zone_target_temperature('{zone_names[0]}', 21.5)")
        print(f"   ember.set_zone_boost('{zone_names[0]}', 23.0, 2)  # 23°C for 2 hours")
        print(f"   ember.set_zone_advance('{zone_names[0]}', True)")
        
        print(f"\n📝 Raw zone data saved to 'zones_data.json'")
        with open('zones_data.json', 'w') as f:
            json.dump(zones, f, indent=2)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Tips:")
        print("   - Check your email/password are correct")
        print("   - Make sure you have zones configured in your EPH Controls system")
        print("   - Ensure your gateway is online")

if __name__ == '__main__':
    discover_zones()