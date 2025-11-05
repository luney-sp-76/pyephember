#!/bin/bash
# Simple Home Assistant Entity Discovery (works without special 'ha' commands)

echo "=========================================="
echo "Home Assistant Entity Discovery"
echo "$(date)"
echo "=========================================="

# Method 1: Check if we're in the HA container/environment
if [ -f "/config/home-assistant.log" ]; then
    echo "✅ Found HA config directory"
    CONFIG_DIR="/config"
elif [ -f "/usr/share/hassio/homeassistant/home-assistant.log" ]; then
    echo "✅ Found HASSIO config directory"  
    CONFIG_DIR="/usr/share/hassio/homeassistant"
else
    echo "❌ Cannot find HA config directory"
    echo "   Try running this from the HA host or container"
    CONFIG_DIR=""
fi

# Method 2: Check .storage/core.entity_registry if available
if [ -n "$CONFIG_DIR" ] && [ -f "$CONFIG_DIR/.storage/core.entity_registry" ]; then
    echo ""
    echo "=== CLIMATE ENTITIES FROM REGISTRY ==="
    echo "Looking for climate entities in entity registry..."
    grep -o '"entity_id":"climate\.[^"]*"' "$CONFIG_DIR/.storage/core.entity_registry" | cut -d'"' -f4 | sort
    
    echo ""
    echo "=== EPH/EMBER ENTITIES FROM REGISTRY ==="
    echo "Looking for EPH/Ember entities..."
    grep -i -o '"entity_id":"[^"]*eph[^"]*"' "$CONFIG_DIR/.storage/core.entity_registry" | cut -d'"' -f4
    grep -i -o '"entity_id":"[^"]*ember[^"]*"' "$CONFIG_DIR/.storage/core.entity_registry" | cut -d'"' -f4
else
    echo "❌ Cannot access entity registry"
fi

# Method 3: Check recent logs for entity mentions
if [ -n "$CONFIG_DIR" ] && [ -f "$CONFIG_DIR/home-assistant.log" ]; then
    echo ""
    echo "=== RECENT ENTITY MENTIONS IN LOGS ==="
    echo "Climate entities mentioned in recent logs:"
    grep -o "climate\.[a-zA-Z0-9_]*" "$CONFIG_DIR/home-assistant.log" | sort | uniq | tail -10
    
    echo ""
    echo "EPH/Ember entities mentioned in logs:"
    grep -i -o "[a-zA-Z0-9_]*\.[a-zA-Z0-9_]*eph[a-zA-Z0-9_]*" "$CONFIG_DIR/home-assistant.log" | sort | uniq | tail -10
    grep -i -o "[a-zA-Z0-9_]*\.[a-zA-Z0-9_]*ember[a-zA-Z0-9_]*" "$CONFIG_DIR/home-assistant.log" | sort | uniq | tail -10
fi

# Method 4: Check what integrations are loaded
if [ -n "$CONFIG_DIR" ] && [ -f "$CONFIG_DIR/.storage/core.config_entries" ]; then
    echo ""
    echo "=== LOADED INTEGRATIONS ==="
    echo "Looking for EPH/Ember integrations..."
    grep -i -o '"domain":"[^"]*eph[^"]*"' "$CONFIG_DIR/.storage/core.config_entries" | cut -d'"' -f4
    grep -i -o '"domain":"[^"]*ember[^"]*"' "$CONFIG_DIR/.storage/core.config_entries" | cut -d'"' -f4
fi

# Method 5: Quick package check
if [ -n "$CONFIG_DIR" ] && [ -d "$CONFIG_DIR/packages" ]; then
    echo ""
    echo "=== PACKAGE FILES ==="
    echo "Heating-related packages found:"
    ls -la "$CONFIG_DIR/packages/"*heating* 2>/dev/null || echo "No heating packages found"
    ls -la "$CONFIG_DIR/packages/"*eph* 2>/dev/null || echo "No EPH packages found" 
fi

echo ""
echo "=========================================="
echo "SUMMARY & NEXT STEPS"
echo "=========================================="
echo "If you found climate entities above:"
echo "1. Note the actual entity names (e.g. climate.eph_thermostat)"
echo "2. Update heating_analytics_package.yaml to use the correct names"
echo "3. Restart Home Assistant"
echo ""
echo "If no climate entities were found:"
echo "1. Check Settings > Devices & Services in HA UI"
echo "2. Look for EPH Controls or similar integration"
echo "3. Add/configure the integration if missing"
echo ""
echo "Entity discovery completed at: $(date)"