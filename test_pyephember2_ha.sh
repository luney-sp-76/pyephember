#!/bin/bash
# PyEphEmber2 Home Assistant Integration Tester
# Run this script via SSH on your Home Assistant system

echo "=========================================="
echo "PyEphEmber2 Home Assistant Integration Test"
echo "Started at: $(date)"
echo "=========================================="

# Function to check if entity exists
check_entity() {
    local entity=$1
    echo ""
    echo "Checking entity: $entity"
    echo "------------------------------------------"
    
    # Use ha command to get entity state
    if ha states get "$entity" > /dev/null 2>&1; then
        echo "✅ Entity exists"
        ha states get "$entity"
    else
        echo "❌ Entity not found"
    fi
}

# Function to get entity attributes in readable format
show_entity_details() {
    local entity=$1
    echo ""
    echo "=========================================="
    echo "DETAILED ANALYSIS: $entity"
    echo "=========================================="
    
    # Get full entity data
    ha states get "$entity" --format json | python3 -c "
import json
import sys

try:
    data = json.load(sys.stdin)
    print(f'Entity ID: {data.get(\"entity_id\", \"unknown\")}')
    print(f'State: {data.get(\"state\", \"unknown\")}')
    print(f'Last Changed: {data.get(\"last_changed\", \"unknown\")}')
    print()
    print('ATTRIBUTES:')
    print('-' * 40)
    
    attributes = data.get('attributes', {})
    for key in sorted(attributes.keys()):
        value = attributes[key]
        print(f'{key:25} = {value}')
    
    print()
    print('HEATING DETECTION ANALYSIS:')
    print('-' * 40)
    
    hvac_action = attributes.get('hvac_action')
    hvac_mode = attributes.get('hvac_mode')  
    current_temp = attributes.get('current_temperature')
    target_temp = attributes.get('temperature')
    state = data.get('state')
    
    print(f'Method 1 - HVAC Action: {hvac_action}')
    print(f'  -> Heating Active: {hvac_action == \"heating\"}')
    
    print(f'Method 2 - Mode + Temp: {hvac_mode}, {current_temp}°C -> {target_temp}°C')
    if current_temp and target_temp:
        try:
            temp_diff = float(target_temp) - float(current_temp)
            heating_needed = hvac_mode == 'heat' and temp_diff > 0.5
            print(f'  -> Temperature Difference: {temp_diff:.1f}°C')
            print(f'  -> Heating Needed: {heating_needed}')
        except (ValueError, TypeError):
            print('  -> Cannot calculate temperature difference')
    
    print(f'Method 3 - Entity State: {state}')
    print(f'  -> State-based Heating: {state == \"heat\"}')
    
    print()
    print('RECOMMENDED DETECTION:')
    if hvac_action:
        is_heating = hvac_action == 'heating'
        print(f'✅ Use hvac_action: {is_heating}')
    elif hvac_mode and current_temp and target_temp:
        try:
            heating = hvac_mode == 'heat' and float(target_temp) > float(current_temp) + 0.5
            print(f'⚠️  Use mode+temp fallback: {heating}')
        except (ValueError, TypeError):
            print('❌ Cannot determine heating status from temperature')
    else:
        print('❌ Limited detection options available')

except json.JSONDecodeError:
    print('Error: Could not parse entity data')
except Exception as e:
    print(f'Error: {e}')
"
}

# Main execution
echo ""
echo "Step 1: Checking core entities..."

# Check if climate.one exists
check_entity "climate.one"

# Check if our heating detection sensor exists
check_entity "binary_sensor.zone_one_heating_active"

# Check heating analytics entities
echo ""
echo "Step 2: Checking heating analytics entities..."
check_entity "counter.zone_one_heating_cycles_today"
check_entity "sensor.zone_one_average_heating_duration"
check_entity "input_number.zone_one_total_heating_time_today"

# Detailed analysis of climate.one
if ha states get "climate.one" > /dev/null 2>&1; then
    show_entity_details "climate.one"
else
    echo ""
    echo "❌ Cannot analyze climate.one - entity not found"
    echo "   Check if PyEphEmber2 integration is working"
fi

# Check if heating detection is working
echo ""
echo "=========================================="
echo "HEATING DETECTION STATUS"
echo "=========================================="

if ha states get "binary_sensor.zone_one_heating_active" > /dev/null 2>&1; then
    HEATING_STATE=$(ha states get "binary_sensor.zone_one_heating_active" --format json | python3 -c "import json, sys; print(json.load(sys.stdin).get('state', 'unknown'))")
    echo "Current heating detection state: $HEATING_STATE"
    
    if [ "$HEATING_STATE" = "on" ]; then
        echo "🔥 HEATING IS CURRENTLY ACTIVE"
    elif [ "$HEATING_STATE" = "off" ]; then
        echo "❄️  HEATING IS CURRENTLY OFF"
    else
        echo "⚠️  HEATING STATE UNKNOWN: $HEATING_STATE"
    fi
else
    echo "❌ Heating detection sensor not configured"
fi

# PyEphEmber2 change checklist
echo ""
echo "=========================================="
echo "PYEPHEMBER2 CHANGE CHECKLIST"
echo "=========================================="

checklist=(
    "1. Check if hvac_action attribute is still 'heating' when active"
    "2. Verify current_temperature and temperature attributes exist"  
    "3. Confirm hvac_mode values (heat/off/auto)"
    "4. Check if entity state changes (heat/off/idle)"
    "5. Look for new attributes added in PyEphEmber2"
    "6. Verify supported_features hasn't changed"
    "7. Check if device_class or unit_of_measurement changed"
)

for item in "${checklist[@]}"; do
    echo "☐ $item"
done

echo ""
echo "=========================================="
echo "NEXT STEPS"
echo "=========================================="
echo "1. Review the attribute analysis above"
echo "2. Compare with previous PyEphEmber behavior"
echo "3. Update heating detection if hvac_action changed"
echo "4. Test the heating analytics dashboard"
echo "5. Check InfluxDB data storage is working"
echo "6. Verify mobile dashboard displays correctly"

echo ""
echo "=========================================="
echo "QUICK TESTS YOU CAN RUN"
echo "=========================================="
echo "# Check recent logbook entries for climate changes:"
echo "ha logs --follow | grep climate.one"
echo ""
echo "# Monitor heating detection in real-time:"
echo "watch 'ha states get binary_sensor.zone_one_heating_active'"
echo ""
echo "# Check all heating-related entities:"
echo "ha states list | grep zone_one"

echo ""
echo "Test completed at: $(date)"