# PyEphEmber2 Quick Diagnostic Commands
# Run these commands via SSH on your Home Assistant system

# Basic entity checks
echo "=== CHECKING CORE ENTITIES ==="
ha states get climate.one
echo ""
ha states get binary_sensor.zone_one_heating_active
echo ""

# Check heating analytics entities  
echo "=== HEATING ANALYTICS ENTITIES ==="
ha states get counter.zone_one_heating_cycles_today
ha states get sensor.zone_one_average_heating_duration
ha states get input_number.zone_one_total_heating_time_today
echo ""

# List all zone_one entities
echo "=== ALL ZONE ONE ENTITIES ==="
ha states list | grep zone_one
echo ""

# Check recent climate changes
echo "=== RECENT CLIMATE ACTIVITY ==="
ha logs --lines 20 | grep climate
echo ""

# Show current heating status
echo "=== CURRENT HEATING STATUS ==="
CLIMATE_STATE=$(ha states get climate.one --format json 2>/dev/null | grep -o '"state":"[^"]*' | cut -d'"' -f4)
HVAC_ACTION=$(ha states get climate.one --format json 2>/dev/null | grep -o '"hvac_action":"[^"]*' | cut -d'"' -f4)
CURRENT_TEMP=$(ha states get climate.one --format json 2>/dev/null | grep -o '"current_temperature":[^,]*' | cut -d':' -f2)
TARGET_TEMP=$(ha states get climate.one --format json 2>/dev/null | grep -o '"temperature":[^,]*' | cut -d':' -f2)

echo "Climate State: $CLIMATE_STATE"
echo "HVAC Action: $HVAC_ACTION" 
echo "Current Temperature: ${CURRENT_TEMP}°C"
echo "Target Temperature: ${TARGET_TEMP}°C"

if [ "$HVAC_ACTION" = "heating" ]; then
    echo "🔥 HEATING IS ACTIVE (hvac_action method)"
elif [ "$CLIMATE_STATE" = "heat" ]; then
    echo "🔥 HEATING DETECTED (state method)"
else
    echo "❄️ HEATING IS OFF"
fi