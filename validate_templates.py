#!/usr/bin/env python3
"""
Template validation - check for common HA template issues
"""

def check_template_issues(filename):
    """Check for common template issues that cause HA errors"""
    
    print(f"🔍 Checking {filename}...")
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
        
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for value_json.get() in REST sensors (should use value_json.field)
            if 'value_json.get(' in line:
                issues.append(f"Line {i}: 'value_json.get()' should be 'value_json.field'")
            
            # Check for unmatched template brackets
            if line.count('{{') != line.count('}}'):
                issues.append(f"Line {i}: Unmatched template brackets {{ }}")
            
            if line.count('{%') != line.count('%}'):
                issues.append(f"Line {i}: Unmatched template brackets")
            
            # Check for stray %} at end of availability templates
            if line.strip() == '%}' and i > 1:
                prev_line = lines[i-2].strip() if i > 1 else ''
                if 'availability:' in prev_line:
                    issues.append(f"Line {i}: Stray template marker after availability")
        
        # Check file ending
        if content.endswith('%}'):
            issues.append("File ends with stray template marker - remove this")
        
        if issues:
            print(f"  ⚠ Found {len(issues)} issues:")
            for issue in issues[:5]:
                print(f"    • {issue}")
            if len(issues) > 5:
                print(f"    • ... and {len(issues) - 5} more")
            return False
        else:
            print(f"  ✓ No template issues found")
            return True
            
    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("🏠 Home Assistant Template Validation")
    print("=" * 40)
    
    files = [
        "fuel_by_home_postcode_working_fixed.yaml",
        "heating_cost_analysis_working.yaml"
    ]
    
    all_good = True
    for filename in files:
        if not check_template_issues(filename):
            all_good = False
        print()
    
    if all_good:
        print("✅ All templates look good!")
        print("Ready for Home Assistant deployment.")
    else:
        print("⚠️ Some templates have issues.")
        print("Fix before deploying to avoid template errors.")
    
    print("\n📋 Deployment checklist:")
    print("1. Copy fuel_by_home_postcode_working_fixed.yaml to HA host")
    print("2. Remove any old fuel_by_home_postcode*.yaml files") 
    print("3. Run fix_fuel_integration.sh on HA host")
    print("4. Restart Home Assistant")
    print("5. Check logs for template errors")

if __name__ == "__main__":
    main()