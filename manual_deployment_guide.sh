#!/bin/bash
# Simple Manual Deployment Guide for SSH Remote Access

echo "=========================================="
echo "🚨 MANUAL PyEphEmber2 Emergency Recovery"
echo "Remote SSH Deployment Guide"
echo "$(date)"
echo "=========================================="

echo ""
echo "📋 STEP 1: LOCATE YOUR HA CONFIG DIRECTORY"
echo "============================================"
echo "Find your Home Assistant config directory. Common locations:"
echo "• /home/homeassistant/.homeassistant/"
echo "• /config/"
echo "• /usr/share/hassio/homeassistant/"
echo "• ~/homeassistant/ (if running as user)"
echo ""
echo "💡 TIP: Look for a directory containing 'configuration.yaml'"

echo ""
echo "📋 STEP 2: COPY EMERGENCY FALLBACK CONFIG"
echo "=========================================="
echo "Copy the emergency fallback file to your HA packages directory:"
echo ""
echo "From your current directory:"
echo "  $(pwd)"
echo ""
echo "Copy this file:"
echo "  pyephember2_heating_detection.yaml"
echo ""
echo "To your HA packages directory (create 'packages' folder if it doesn't exist):"
echo "  [YOUR_HA_CONFIG]/packages/pyephember2_heating_detection.yaml"
echo ""
echo "Example commands (adjust paths as needed):"
echo "  sudo mkdir -p /home/homeassistant/.homeassistant/packages"
echo "  sudo cp pyephember2_heating_detection.yaml /home/homeassistant/.homeassistant/packages/"
echo "  # OR via scp if remote:"
echo "  scp pyephember2_heating_detection.yaml user@ha-host:/path/to/config/packages/"

echo ""
echo "📋 STEP 3: VERIFY PACKAGES CONFIGURATION"
echo "========================================"
echo "Ensure your configuration.yaml includes packages:"
echo ""
echo "# In configuration.yaml, add or verify this line exists:"
echo "homeassistant:"
echo "  packages: !include_dir_named packages"
echo ""
echo "OR if using a different structure:"
echo "packages: !include_dir_named packages"

echo ""
echo "📋 STEP 4: CHECK CURRENT CLIMATE ENTITY STATUS"
echo "=============================================="
echo "Run this to check what climate entities exist:"
echo ""

# Create a simple entity check that works from current directory
cat > simple_climate_check.sh << 'EOF'
#!/bin/bash
echo "=== SIMPLE CLIMATE ENTITY CHECK ==="
echo "Attempting to find HA config and check climate entities..."

# Try to find HA config directory
for CONFIG_DIR in "/config" "/home/homeassistant/.homeassistant" "/usr/share/hassio/homeassistant"; do
    if [ -f "$CONFIG_DIR/configuration.yaml" ]; then
        echo "✅ Found HA config at: $CONFIG_DIR"
        
        if [ -f "$CONFIG_DIR/.storage/core.entity_registry" ]; then
            echo ""
            echo "Climate entities in registry:"
            grep -o '"entity_id":"climate\.[^"]*"' "$CONFIG_DIR/.storage/core.entity_registry" | cut -d'"' -f4 | sort
            
            echo ""
            echo "Checking specifically for climate.one:"
            if grep -q '"entity_id":"climate.one"' "$CONFIG_DIR/.storage/core.entity_registry"; then
                echo "✅ climate.one exists"
            else
                echo "❌ climate.one missing"
            fi
        else
            echo "❌ Cannot access entity registry"
        fi
        break
    fi
done
EOF

chmod +x simple_climate_check.sh
echo "  ./simple_climate_check.sh"

echo ""
echo "📋 STEP 5: RESTART HOME ASSISTANT"
echo "================================="
echo "After copying the files, restart HA to load the emergency sensors:"
echo "• Via HA UI: Settings > System > Restart"
echo "• Via command line: sudo systemctl restart home-assistant@homeassistant"
echo "• Via Docker: docker restart homeassistant"

echo ""
echo "📋 STEP 6: VERIFY EMERGENCY SENSORS LOADED"
echo "=========================================="
echo "After restart, check Developer Tools > States for these new entities:"
echo "• binary_sensor.zone_one_heating_active (enhanced with fallbacks)"
echo "• binary_sensor.zone_one_heating_api_check" 
echo "• binary_sensor.zone_one_heating_trend"
echo "• sensor.climate_one_debug"
echo "• sensor.pyephember2_debug_status"

echo ""
echo "📋 STEP 7: INVESTIGATE INTEGRATION STATUS"
echo "========================================"
echo "Check Settings > Devices & Services in HA web interface:"
echo "• Look for EPH Controls, Ember, or PyEphEmber integration"
echo "• Check if it shows errors or needs reconfiguration"
echo "• Note any new climate entity names"

echo ""
echo "🎯 SUMMARY"
echo "=========="
echo "Files created:"
echo "✅ pyephember2_heating_detection.yaml - Emergency fallback config"
echo "✅ simple_climate_check.sh - Quick entity status check"
echo "✅ emergency_recovery.sh - This deployment guide"
echo ""
echo "What the emergency config provides:"
echo "🔄 Multiple heating detection methods (hvac_action, temp diff, state)"
echo "🐛 Debug sensors to understand PyEphEmber2 changes"
echo "📊 Logging automations to track entity changes"
echo "🔧 Fallback binary sensors if main detection fails"
echo ""
echo "⚠️  CRITICAL: This emergency config will keep your heating analytics"
echo "   working even if PyEphEmber2 changed how it reports heating status!"