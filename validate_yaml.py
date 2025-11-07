#!/usr/bin/env python3
"""
YAML Validation Script - Check syntax without external dependencies
"""

def validate_yaml_basic(filename):
    """Basic YAML validation without importing yaml library"""
    print(f"🔍 Checking {filename}...")
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        # Basic checks
        lines = content.split('\n')
        issues = []
        
        # Check for common YAML issues
        in_template_section = False
        in_sensor_section = False
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # Track sections
            if stripped.startswith('template:'):
                in_template_section = True
                in_sensor_section = False
            elif stripped.startswith('sensor:'):
                if in_template_section:
                    in_sensor_section = True
                else:
                    in_template_section = False
                    in_sensor_section = True
            
            # Check for platform in template section
            if in_template_section and in_sensor_section and 'platform:' in stripped:
                issues.append(f"Line {i}: 'platform:' not allowed in template section")
            
            # Check for basic YAML structure
            if stripped and not stripped.startswith('#'):
                if ':' in stripped and not stripped.startswith('-'):
                    key_part = stripped.split(':')[0].strip()
                    if ' ' in key_part and not key_part.startswith('"') and not key_part.startswith("'"):
                        issues.append(f"Line {i}: Unquoted key with spaces: '{key_part}'")
        
        if issues:
            print(f"  ⚠ Found {len(issues)} potential issues:")
            for issue in issues[:5]:  # Show first 5
                print(f"    • {issue}")
            if len(issues) > 5:
                print(f"    • ... and {len(issues) - 5} more")
            return False
        else:
            print(f"  ✓ Basic structure looks good")
            print(f"  ✓ {len(lines)} lines, {len(content)} characters")
            return True
            
    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        return False
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")
        return False

def main():
    print("🏠 Home Assistant YAML Validation")
    print("=" * 40)
    
    files_to_check = [
        "fuel_by_home_postcode_working_fixed.yaml",
        "heating_cost_analysis_working.yaml",
        "heating_cost_dashboard.yaml"
    ]
    
    all_good = True
    for filename in files_to_check:
        if not validate_yaml_basic(filename):
            all_good = False
        print()
    
    if all_good:
        print("✅ All files passed basic validation!")
        print("Ready for Home Assistant deployment.")
    else:
        print("⚠️ Some files have issues.")
        print("Please fix before deploying to Home Assistant.")

if __name__ == "__main__":
    main()