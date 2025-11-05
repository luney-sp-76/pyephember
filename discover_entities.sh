#!/bin/bash
# PyEphEmber2 Discovery Script - Find what entities actually exist

echo "=========================================="
echo "PyEphEmber2 Entity Discovery"
echo "Started at: $(date)"
echo "=========================================="

# Step 1: Check if ANY climate entities exist
echo ""
echo "=== STEP 1: ALL CLIMATE ENTITIES ==="
echo "Looking for any climate entities..."
CLIMATE_ENTITIES=$(ha states list | grep "^climate\." || echo "None found")
echo "$CLIMATE_ENTITIES"

if [ "$CLIMATE_ENTITIES" = "None found" ]; then
    echo "❌ No climate entities found at all!"
    echo "   PyEphEmber2 integration may not be loaded"
else
    echo "✅ Found climate entities - checking each one..."
    echo "$CLIMATE_ENTITIES" | while read entity; do
        if [ -n "$entity" ]; then
            echo ""
            echo "--- Details for $entity ---"
            ha states get "$entity"
        fi
    done
fi

# Step 2: Check for EPH/Ember related entities
echo ""
echo "=== STEP 2: EPH/EMBER RELATED ENTITIES ==="
echo "Looking for EPH or Ember related entities..."
EPH_ENTITIES=$(ha states list | grep -i "eph\|ember" || echo "None found")
echo "$EPH_ENTITIES"

# Step 3: Check integrations
echo ""
echo "=== STEP 3: LOADED INTEGRATIONS ==="
echo "Checking what integrations are loaded..."
ha integrations list | grep -i "eph\|ember\|climate" || echo "No EPH/Ember integrations found"

# Step 4: Check configuration errors
echo ""
echo "=== STEP 4: RECENT CONFIGURATION ERRORS ==="
echo "Looking for configuration errors..."
ha logs --lines 50 | grep -i "error\|fail\|package" | grep -v "DEBUG" | tail -10

# Step 5: Check if packages are loaded
echo ""
echo "=== STEP 5: PACKAGE STATUS ==="
echo "Checking if packages directory is being loaded..."
ha logs --lines 100 | grep -i "package" | tail -5

# Step 6: List ALL entities to see what exists
echo ""
echo "=== STEP 6: SAMPLE OF ALL ENTITIES ==="
echo "Here are some entities that DO exist (first 20):"
ha states list | head -20

echo ""
echo "=========================================="
echo "DIAGNOSIS SUMMARY"
echo "=========================================="

if ha states list | grep -q "^climate\."; then
    echo "✅ Climate platform is working"
    echo "   Entity name may have changed in PyEphEmber2"
    echo "   Check the climate entities listed above"
else
    echo "❌ No climate entities found"
    echo "   PyEphEmber2 integration is not working"
fi

echo ""
echo "=========================================="
echo "IMMEDIATE ACTIONS TO TRY"
echo "=========================================="
echo "1. Check Home Assistant > Settings > Devices & Services"
echo "2. Look for EPH Controls or PyEphEmber integration"
echo "3. If missing, re-add the integration"
echo "4. Check configuration.yaml for any errors"
echo "5. Restart Home Assistant if needed"

echo ""
echo "=========================================="
echo "COMMANDS TO RUN NEXT"
echo "=========================================="
echo "# Check integration status:"
echo "ha integrations list"
echo ""
echo "# Check for configuration errors:"
echo "ha config check"
echo ""
echo "# Watch logs in real-time:"
echo "ha logs --follow"
echo ""
echo "# If you find climate entities with different names:"
echo "ha states get climate.ACTUAL_ENTITY_NAME"

echo ""
echo "Discovery completed at: $(date)"