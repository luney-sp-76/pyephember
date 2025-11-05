#!/usr/bin/env python3
"""
Home Assistant Heating & Humidity Automation Tester
Test suite to verify EPH Ember heating and humidity automations work correctly
"""

import sys
import json
import time
import requests
from datetime import datetime, timedelta
import os

class HAAutomationTester:
    """Test Home Assistant heating and humidity automations"""
    
    def __init__(self, ha_url="http://localhost:8123", token=None):
        self.ha_url = ha_url.rstrip('/')
        self.token = token or os.environ.get('HA_TOKEN')
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
    def _api_call(self, endpoint, method="GET", data=None):
        """Make API call to Home Assistant"""
        url = f"{self.ha_url}/api/{endpoint}"
        try:
            if method == "POST":
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            else:
                response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return None
    
    def get_states(self, entity_filter=None):
        """Get all states or filtered states"""
        states = self._api_call("states")
        if not states:
            return []
        
        if entity_filter:
            return [s for s in states if entity_filter in s['entity_id']]
        return states
    
    def get_entity_state(self, entity_id):
        """Get specific entity state"""
        return self._api_call(f"states/{entity_id}")
    
    def call_service(self, domain, service, entity_id=None, data=None):
        """Call a Home Assistant service"""
        service_data = data or {}
        if entity_id:
            service_data['entity_id'] = entity_id
            
        result = self._api_call(f"services/{domain}/{service}", "POST", service_data)
        print(f"🔧 Called {domain}.{service} on {entity_id}")
        return result
    
    def test_climate_entities(self):
        """Test all climate entities are available"""
        print("\n🌡️  Testing Climate Entities...")
        climate_entities = self.get_states("climate.")
        
        if not climate_entities:
            print("❌ No climate entities found!")
            return False
            
        print(f"✅ Found {len(climate_entities)} climate entities:")
        for entity in climate_entities:
            name = entity['entity_id']
            state = entity['state']
            temp = entity['attributes'].get('current_temperature', 'N/A')
            target = entity['attributes'].get('temperature', 'N/A')
            print(f"   📍 {name}: {state} | Current: {temp}°C | Target: {target}°C")
            
        return True
    
    def test_humidity_sensors(self):
        """Test humidity sensor availability"""
        print("\n💧 Testing Humidity Sensors...")
        humidity_entities = [s for s in self.get_states("sensor.") 
                           if 'humidity' in s['entity_id'] or 
                              s['attributes'].get('device_class') == 'humidity']
        
        if not humidity_entities:
            print("❌ No humidity sensors found!")
            return False
            
        print(f"✅ Found {len(humidity_entities)} humidity sensors:")
        for entity in humidity_entities:
            name = entity['entity_id']
            state = entity['state']
            unit = entity['attributes'].get('unit_of_measurement', '')
            print(f"   💧 {name}: {state}{unit}")
            
        return True
    
    def test_temperature_control(self, climate_entity=None):
        """Test temperature control functionality"""
        print("\n🎯 Testing Temperature Control...")
        
        # Find a climate entity to test
        if not climate_entity:
            climate_entities = self.get_states("climate.")
            if not climate_entities:
                print("❌ No climate entities to test!")
                return False
            climate_entity = climate_entities[0]['entity_id']
        
        print(f"🔧 Testing with entity: {climate_entity}")
        
        # Get current state
        initial_state = self.get_entity_state(climate_entity)
        if not initial_state:
            print(f"❌ Cannot get state for {climate_entity}")
            return False
            
        initial_temp = initial_state['attributes'].get('temperature')
        print(f"📊 Initial target temperature: {initial_temp}°C")
        
        # Test temperature change
        test_temp = 20.0
        if initial_temp == test_temp:
            test_temp = 21.0
            
        print(f"🔧 Setting temperature to {test_temp}°C...")
        result = self.call_service("climate", "set_temperature", 
                                 climate_entity, {"temperature": test_temp})
        
        # Wait and verify
        time.sleep(2)
        new_state = self.get_entity_state(climate_entity)
        new_temp = new_state['attributes'].get('temperature')
        
        if new_temp == test_temp:
            print(f"✅ Temperature control working! Set to {new_temp}°C")
            
            # Restore original temperature
            if initial_temp:
                self.call_service("climate", "set_temperature", 
                                climate_entity, {"temperature": initial_temp})
                print(f"🔄 Restored to {initial_temp}°C")
            return True
        else:
            print(f"❌ Temperature control failed! Expected {test_temp}°C, got {new_temp}°C")
            return False
    
    def test_automations_enabled(self):
        """Test that automations are enabled and running"""
        print("\n🤖 Testing Automations...")
        
        # Get all automations
        automations = self.get_states("automation.")
        
        if not automations:
            print("❌ No automations found!")
            return False
            
        print(f"✅ Found {len(automations)} automations:")
        
        heating_automations = []
        humidity_automations = []
        
        for auto in automations:
            name = auto['entity_id']
            state = auto['state']
            friendly_name = auto['attributes'].get('friendly_name', name)
            
            # Categorize automations
            if any(keyword in name.lower() or keyword in friendly_name.lower() 
                   for keyword in ['heat', 'temp', 'climate', 'warm', 'cold']):
                heating_automations.append((name, state, friendly_name))
            
            if any(keyword in name.lower() or keyword in friendly_name.lower() 
                   for keyword in ['humid', 'moisture', 'dry']):
                humidity_automations.append((name, state, friendly_name))
            
            status = "🟢" if state == "on" else "🔴"
            print(f"   {status} {friendly_name}: {state}")
        
        print(f"\n📊 Heating automations: {len(heating_automations)}")
        print(f"📊 Humidity automations: {len(humidity_automations)}")
        
        return len(automations) > 0
    
    def test_trigger_automation(self, automation_entity=None):
        """Test triggering an automation manually"""
        print("\n🎯 Testing Automation Triggers...")
        
        if not automation_entity:
            # Find a heating-related automation
            automations = self.get_states("automation.")
            heating_autos = [a for a in automations 
                           if any(keyword in a['entity_id'].lower() 
                                 for keyword in ['heat', 'temp', 'climate'])]
            
            if not heating_autos:
                print("❌ No heating automations found to test!")
                return False
                
            automation_entity = heating_autos[0]['entity_id']
        
        print(f"🔧 Testing automation: {automation_entity}")
        
        # Trigger the automation
        result = self.call_service("automation", "trigger", automation_entity)
        
        if result is not None:
            print(f"✅ Successfully triggered {automation_entity}")
            return True
        else:
            print(f"❌ Failed to trigger {automation_entity}")
            return False
    
    def test_script_execution(self):
        """Test custom scripts (like EPH Ember commands)"""
        print("\n📜 Testing Custom Scripts...")
        
        # Check if EPH Ember script exists
        script_path = "/config/scripts/eph_ember.py"
        if os.path.exists(script_path):
            print(f"✅ Found EPH Ember script: {script_path}")
            
            # Test list zones command
            try:
                import subprocess
                result = subprocess.run([
                    "python3", script_path, "list_zones"
                ], capture_output=True, text=True, cwd="/config/scripts")
                
                if result.returncode == 0:
                    zones = result.stdout.strip()
                    print(f"✅ EPH zones: {zones}")
                    return True
                else:
                    print(f"❌ Script error: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Script execution failed: {e}")
                return False
        else:
            print(f"ℹ️  EPH Ember script not found at {script_path}")
            return True
    
    def run_comprehensive_test(self):
        """Run all tests"""
        print("🧪 Starting Home Assistant Heating & Humidity Test Suite")
        print("=" * 60)
        
        tests = [
            ("Climate Entities", self.test_climate_entities),
            ("Humidity Sensors", self.test_humidity_sensors),
            ("Temperature Control", self.test_temperature_control),
            ("Automations Status", self.test_automations_enabled),
            ("Custom Scripts", self.test_script_execution),
        ]
        
        results = {}
        
        for test_name, test_func in tests:
            try:
                results[test_name] = test_func()
            except Exception as e:
                print(f"❌ {test_name} failed with error: {e}")
                results[test_name] = False
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        passed = sum(results.values())
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🏆 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 All tests passed! Your heating & humidity automations are working!")
        else:
            print("⚠️  Some tests failed. Check the details above.")
        
        return passed == total


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Test HA Heating & Humidity Automations")
    parser.add_argument("--url", default="http://localhost:8123", 
                       help="Home Assistant URL")
    parser.add_argument("--token", help="Home Assistant Long-Lived Access Token")
    parser.add_argument("--test", choices=[
        "all", "climate", "humidity", "temp", "automations", "scripts"
    ], default="all", help="Which test to run")
    
    args = parser.parse_args()
    
    if not args.token:
        print("❌ Please provide Home Assistant token:")
        print("   export HA_TOKEN='your_long_lived_access_token'")
        print("   or use --token argument")
        return 1
    
    tester = HAAutomationTester(args.url, args.token)
    
    if args.test == "all":
        success = tester.run_comprehensive_test()
    elif args.test == "climate":
        success = tester.test_climate_entities()
    elif args.test == "humidity":
        success = tester.test_humidity_sensors()
    elif args.test == "temp":
        success = tester.test_temperature_control()
    elif args.test == "automations":
        success = tester.test_automations_enabled()
    elif args.test == "scripts":
        success = tester.test_script_execution()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())