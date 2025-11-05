#!/usr/bin/env python3
"""
Quick Home Assistant Automation Tester
Simple tests that work within HA's environment
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def test_pyephember_installation():
    """Test if PyEphEmber is properly installed"""
    print("🔥 Testing PyEphEmber Installation...")
    
    try:
        import pyephember
        print(f"✅ PyEphEmber imported successfully")
        
        # Try to create an EphEmber instance (will fail without credentials, but import works)
        from pyephember.pyephember import EphEmber
        print(f"✅ EphEmber class available")
        return True
        
    except ImportError as e:
        print(f"❌ PyEphEmber not installed: {e}")
        print("💡 Run: pip install pyephember")
        return False
    except Exception as e:
        print(f"⚠️  PyEphEmber import issue: {e}")
        return False

def test_eph_credentials():
    """Test if EPH credentials are configured"""
    print("\n🔐 Testing EPH Credentials...")
    
    email = os.environ.get('EPH_EMAIL')
    password = os.environ.get('EPH_PASSWORD')
    
    if email and password:
        print(f"✅ EPH credentials configured")
        print(f"   Email: {email}")
        print(f"   Password: {'*' * len(password)}")
        return True
    else:
        print("❌ EPH credentials not set")
        print("💡 Set environment variables:")
        print("   export EPH_EMAIL='your-email@example.com'")
        print("   export EPH_PASSWORD='your-password'")
        return False

def test_eph_connection():
    """Test actual connection to EPH Ember API"""
    print("\n🌐 Testing EPH Ember Connection...")
    
    if not test_pyephember_installation():
        return False
        
    if not test_eph_credentials():
        return False
    
    try:
        from pyephember.pyephember import EphEmber
        
        email = os.environ.get('EPH_EMAIL')
        password = os.environ.get('EPH_PASSWORD')
        
        print("🔌 Attempting connection...")
        ember = EphEmber(email, password)
        
        print("📋 Getting zone names...")
        zones = ember.get_zone_names()
        
        print(f"✅ Connection successful!")
        print(f"🏠 Found {len(zones)} zones: {', '.join(zones)}")
        
        # Test getting temperature from first zone
        if zones:
            first_zone = zones[0]
            temp = ember.get_zone_temperature(first_zone)
            target = ember.get_zone_target_temperature(first_zone)
            print(f"🌡️  {first_zone}: {temp}°C → {target}°C")
        
        return True
        
    except Exception as e:
        print(f"❌ EPH connection failed: {e}")
        return False

def test_home_assistant_files():
    """Test Home Assistant configuration files"""
    print("\n📁 Testing Home Assistant Files...")
    
    config_path = Path("/config")
    if not config_path.exists():
        print("❌ /config directory not found")
        return False
    
    files_to_check = [
        "configuration.yaml",
        "automations.yaml", 
        "scripts.yaml",
        "secrets.yaml"
    ]
    
    found_files = []
    for file in files_to_check:
        file_path = config_path / file
        if file_path.exists():
            print(f"✅ {file} exists ({file_path.stat().st_size} bytes)")
            found_files.append(file)
        else:
            print(f"⚠️  {file} not found")
    
    # Check for custom components
    custom_components = config_path / "custom_components"
    if custom_components.exists():
        components = list(custom_components.iterdir())
        print(f"🔌 {len(components)} custom components found")
        for comp in components:
            if comp.is_dir():
                print(f"   • {comp.name}")
    
    return len(found_files) > 0

def test_script_files():
    """Test our custom script files"""
    print("\n📜 Testing Custom Script Files...")
    
    scripts_path = Path("/config/scripts")
    if not scripts_path.exists():
        print("❌ /config/scripts directory not found")
        print("💡 Create it: mkdir -p /config/scripts")
        return False
    
    script_files = [
        "eph_ember.py",
        "test_automations.sh"
    ]
    
    found_scripts = []
    for script in script_files:
        script_path = scripts_path / script
        if script_path.exists():
            print(f"✅ {script} exists ({script_path.stat().st_size} bytes)")
            found_scripts.append(script)
        else:
            print(f"⚠️  {script} not found")
    
    return len(found_scripts) > 0

def test_ha_services():
    """Test Home Assistant service availability"""
    print("\n🏠 Testing Home Assistant Services...")
    
    try:
        # Try to call HA CLI if available
        result = subprocess.run(['ha', 'info'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ Home Assistant CLI available")
            print("📊 HA Info:")
            for line in result.stdout.split('\n')[:5]:  # First 5 lines
                if line.strip():
                    print(f"   {line}")
            return True
        else:
            print("⚠️  HA CLI not responding")
            
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("⚠️  HA CLI not available")
    
    # Alternative: check for HA processes
    try:
        result = subprocess.run(['pgrep', '-f', 'homeassistant'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Home Assistant process running")
            return True
        else:
            print("❌ Home Assistant process not found")
            
    except Exception as e:
        print(f"⚠️  Cannot check HA process: {e}")
    
    return False

def run_quick_automation_test():
    """Run a quick test of automation functionality"""
    print("\n🤖 Quick Automation Test...")
    
    # Check if we can access zone info
    if test_eph_connection():
        try:
            from pyephember.pyephember import EphEmber
            
            email = os.environ.get('EPH_EMAIL')
            password = os.environ.get('EPH_PASSWORD')
            ember = EphEmber(email, password)
            zones = ember.get_zone_names()
            
            if zones:
                first_zone = zones[0]
                print(f"🎯 Testing with zone: {first_zone}")
                
                # Get current state
                current_temp = ember.get_zone_temperature(first_zone)
                target_temp = ember.get_zone_target_temperature(first_zone)
                is_active = ember.is_zone_active(first_zone)
                
                print(f"📊 Current state:")
                print(f"   Temperature: {current_temp}°C")
                print(f"   Target: {target_temp}°C")
                print(f"   Active: {'Yes' if is_active else 'No'}")
                
                print("✅ Zone data retrieval working!")
                return True
            
        except Exception as e:
            print(f"❌ Automation test failed: {e}")
            
    return False

def main():
    """Run all tests"""
    print("🧪 Quick Home Assistant Heating Test")
    print("=" * 40)
    
    tests = [
        ("PyEphEmber Installation", test_pyephember_installation),
        ("EPH Credentials", test_eph_credentials), 
        ("EPH Connection", test_eph_connection),
        ("HA Configuration Files", test_home_assistant_files),
        ("Custom Scripts", test_script_files),
        ("HA Services", test_ha_services),
        ("Quick Automation Test", run_quick_automation_test)
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS")
    print("=" * 40)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")
    
    print(f"\n🏆 {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! Your setup looks good!")
    elif passed >= total * 0.7:
        print("⚠️  Most tests passed. Check failed items above.")
    else:
        print("❌ Many tests failed. Setup needs attention.")
    
    return passed >= total * 0.7

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)