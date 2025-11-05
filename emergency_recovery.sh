#!/bin/bash
# Emergency PyEphEmber2 Diagnostic and Recovery Script

echo "=========================================="
echo "🚨 EMERGENCY PyEphEmber2 Diagnostic"
echo "$(date)"
echo "=========================================="

# Step 1: Copy emergency fallback config
echo "📋 Deploying emergency fallback configuration..."
if [ -f "pyephember2_heating_detection.yaml" ]; then
    echo "Copying pyephember2_heating_detection.yaml to HA packages..."
    # Copy to Home Assistant packages directory via SSH/remote access
    if [ -d "/home/homeassistant/.homeassistant/packages" ]; then
        cp pyephember2_heating_detection.yaml /home/homeassistant/.homeassistant/packages/
        echo "✅ Emergency fallback deployed to /home/homeassistant/.homeassistant/packages/"
    elif [ -d "/usr/share/hassio/homeassistant/packages" ]; then
        cp pyephember2_heating_detection.yaml /usr/share/hassio/homeassistant/packages/
        echo "✅ Emergency fallback deployed to /usr/share/hassio/homeassistant/packages/"
    else
        echo "⚠️  HA packages directory not found. Manual copy required:"
        echo "    scp pyephember2_heating_detection.yaml your-ha-host:/path/to/config/packages/"
        echo "    OR copy via file manager to your HA config/packages/ directory"
    fi
else
    echo "❌ pyephember2_heating_detection.yaml not found in current directory"
fi

# Step 2: Check current climate entity status
echo ""
echo "🔍 CURRENT CLIMATE ENTITY STATUS"
echo "=================================="

# Check if we're in HA environment or have SSH access
if [ -f "/config/home-assistant.log" ]; then
    CONFIG_DIR="/config"
elif [ -f "/usr/share/hassio/homeassistant/home-assistant.log" ]; then
    CONFIG_DIR="/usr/share/hassio/homeassistant"
elif [ -f "/home/homeassistant/.homeassistant/home-assistant.log" ]; then
    CONFIG_DIR="/home/homeassistant/.homeassistant"
else
    echo "❌ HA config directory not accessible from current location"
    echo "    You may need to run this directly on the HA host or via SSH"
    CONFIG_DIR=""
fi

if [ -n "$CONFIG_DIR" ]; then
    # Check entity registry for climate entities
    echo "Climate entities in registry:"
    if [ -f "$CONFIG_DIR/.storage/core.entity_registry" ]; then
        grep -o '"entity_id":"climate\.[^"]*"' "$CONFIG_DIR/.storage/core.entity_registry" | cut -d'"' -f4 | sort
    fi
    
    # Check recent logs for climate mentions
    echo ""
    echo "Recent climate entity activity in logs:"
    if [ -f "$CONFIG_DIR/home-assistant.log" ]; then
        echo "Checking for climate.one:"
        grep -i "climate.one" "$CONFIG_DIR/home-assistant.log" | tail -3
        echo ""
        echo "Checking for climate.castle_thermostat:"
        grep -i "climate.castle_thermostat" "$CONFIG_DIR/home-assistant.log" | tail -3
    fi
    
    # Check for ephember integration status
    echo ""
    echo "EPH/Ember integration status:"
    if [ -f "$CONFIG_DIR/home-assistant.log" ]; then
        grep -i "ephember\|eph.*ember" "$CONFIG_DIR/home-assistant.log" | tail -5
    fi
fi

# Step 3: Emergency instructions
echo ""
echo "🆘 EMERGENCY RECOVERY STEPS"
echo "============================"
echo ""
echo "IMMEDIATE ACTIONS REQUIRED:"
echo ""
echo "1. 📁 COPY FILES TO HA PACKAGES:"
echo "   - Copy pyephember2_heating_detection.yaml to /config/packages/"
echo "   - This provides multiple heating detection methods"
echo ""
echo "2. 🔄 RESTART HOME ASSISTANT:"
echo "   - Settings > System > Restart"
echo "   - This loads the emergency fallback sensors"
echo ""
echo "3. 🕵️ CHECK INTEGRATION STATUS:"
echo "   - Settings > Devices & Services"
echo "   - Look for EPH Controls or Ember integration"
echo "   - Check if it shows any errors or needs reconfiguration"
echo ""
echo "4. 🔍 INVESTIGATE PYEPHEMBER2 CHANGES:"
echo "   - Check if integration needs updating"
echo "   - Look for new entity names in Developer Tools > States"
echo "   - Check integration logs for errors"
echo ""
echo "5. 📊 VERIFY FALLBACK SENSORS:"
echo "   After restart, check for these new entities:"
echo "   - binary_sensor.zone_one_heating_active (enhanced)"
echo "   - binary_sensor.zone_one_heating_api_check"
echo "   - binary_sensor.zone_one_heating_trend"
echo "   - sensor.climate_one_debug"
echo "   - sensor.pyephember2_debug_status"
echo ""
echo "6. 🔧 UPDATE MAIN PACKAGE IF NEEDED:"
echo "   If climate.one is completely gone, we'll need to:"
echo "   - Find the new entity name"
echo "   - Update heating_analytics_package.yaml"
echo "   - Update heating_mobile_dashboard.yaml"
echo ""

# Step 4: Create emergency entity check script
echo ""
echo "📝 CREATING EMERGENCY ENTITY CHECK SCRIPT"
echo "==========================================="

cat > emergency_entity_check.sh << 'EOF'
#!/bin/bash
# Emergency entity status check
echo "=== EMERGENCY ENTITY STATUS CHECK ==="
echo "$(date)"
echo ""

# Method 1: Check if climate.one still exists in registry
# Try different possible HA config locations
for CONFIG_PATH in "/config" "/usr/share/hassio/homeassistant" "/home/homeassistant/.homeassistant"; do
    if [ -f "$CONFIG_PATH/.storage/core.entity_registry" ]; then
        echo "🔍 Checking for climate.one in entity registry ($CONFIG_PATH)..."
        if grep -q '"entity_id":"climate.one"' "$CONFIG_PATH/.storage/core.entity_registry"; then
            echo "✅ climate.one still exists in registry"
        else
            echo "❌ climate.one NOT found in registry"
            echo "   Looking for alternative climate entities..."
            grep -o '"entity_id":"climate\.[^"]*"' "$CONFIG_PATH/.storage/core.entity_registry" | cut -d'"' -f4
        fi
        FOUND_CONFIG="$CONFIG_PATH"
        break
    fi
done

# Method 2: Check current state files
if [ -n "$FOUND_CONFIG" ] && [ -f "$FOUND_CONFIG/.storage/core.restore_state" ]; then
    echo ""
    echo "🔍 Checking restore state for climate entities..."
    grep -o '"entity_id":"climate\.[^"]*"' "$FOUND_CONFIG/.storage/core.restore_state" | cut -d'"' -f4 | sort | uniq
fi

# Method 3: Check recent logs for any climate activity
if [ -n "$FOUND_CONFIG" ] && [ -f "$FOUND_CONFIG/home-assistant.log" ]; then
    echo ""
    echo "🔍 Recent climate entity log activity..."
    grep "climate\." "$FOUND_CONFIG/home-assistant.log" | tail -10
fi

echo ""
echo "=== NEXT STEPS ==="
echo "1. If climate.one exists but not working: Check EPH integration status"
echo "2. If climate.one missing: Look for new entity names above"
echo "3. Deploy emergency fallback configuration"
echo "4. Restart Home Assistant to load fallback sensors"

EOF

chmod +x emergency_entity_check.sh
echo "✅ Created emergency_entity_check.sh"

echo ""
echo "🎯 SUMMARY"
echo "=========="
echo "✅ Emergency diagnostic completed"
echo "✅ Recovery instructions provided"
echo "✅ Fallback configuration ready"
echo "✅ Emergency entity check script created"
echo ""
echo "⚠️  NEXT: Copy pyephember2_heating_detection.yaml to /config/packages/ and restart HA"
echo ""
echo "📞 This provides multiple heating detection methods as backup!"