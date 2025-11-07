#!/bin/bash
# Cleanup and Fix Fuel Integration
# Run this on your Home Assistant host to fix the template errors

echo "🔧 Fixing Fuel Integration Template Errors"
echo "=========================================="

# Configuration
HA_CONFIG_DIR="/root/config"
PACKAGES_DIR="$HA_CONFIG_DIR/packages"

echo "📁 Current packages directory contents:"
ls -la "$PACKAGES_DIR/" | grep fuel || echo "  No fuel-related files found"

# Remove old broken files
echo ""
echo "🗑️ Removing old/broken files..."
if [ -f "$PACKAGES_DIR/fuel_by_home_postcode_working.yaml" ]; then
    rm "$PACKAGES_DIR/fuel_by_home_postcode_working.yaml"
    echo "  ✓ Removed fuel_by_home_postcode_working.yaml"
fi

if [ -f "$PACKAGES_DIR/fuel_by_home_postcode.yaml" ]; then
    rm "$PACKAGES_DIR/fuel_by_home_postcode.yaml"
    echo "  ✓ Removed old fuel_by_home_postcode.yaml"
fi

# Copy the fixed file
echo ""
echo "📦 Installing fixed configuration..."
if [ -f "fuel_by_home_postcode_working_fixed.yaml" ]; then
    cp fuel_by_home_postcode_working_fixed.yaml "$PACKAGES_DIR/fuel_by_home_postcode.yaml"
    echo "  ✓ Installed fuel_by_home_postcode_working_fixed.yaml → fuel_by_home_postcode.yaml"
else
    echo "  ✗ fuel_by_home_postcode_working_fixed.yaml not found!"
    echo "    Please copy this file to your HA host first"
    exit 1
fi

# Install cost analysis
if [ -f "heating_cost_analysis_working.yaml" ]; then
    cp heating_cost_analysis_working.yaml "$PACKAGES_DIR/heating_cost_analysis.yaml"
    echo "  ✓ Installed heating_cost_analysis_working.yaml → heating_cost_analysis.yaml"
else
    echo "  ⚠ heating_cost_analysis_working.yaml not found"
fi

# Validate the new configuration
echo ""
echo "🔍 Validating new configuration..."
if [ -f "$PACKAGES_DIR/fuel_by_home_postcode.yaml" ]; then
    lines=$(wc -l < "$PACKAGES_DIR/fuel_by_home_postcode.yaml")
    echo "  ✓ fuel_by_home_postcode.yaml: $lines lines"
    
    # Check for common issues
    if grep -q "value_json\.get" "$PACKAGES_DIR/fuel_by_home_postcode.yaml"; then
        echo "  ⚠ Found value_json.get() - this may cause template errors"
    else
        echo "  ✓ No value_json.get() found - should work correctly"
    fi
    
    # Check for extra template markers
    if grep -q "%}" "$PACKAGES_DIR/fuel_by_home_postcode.yaml" | tail -1 | grep -q "^[[:space:]]*%}"; then
        echo "  ⚠ Found stray %} at end of file"
    else
        echo "  ✓ No stray template markers found"
    fi
else
    echo "  ✗ fuel_by_home_postcode.yaml not found after copy!"
    exit 1
fi

echo ""
echo "📊 Expected entities after restart:"
echo "  • sensor.home_postcode_lookup"
echo "  • sensor.asda_fuel_raw"
echo "  • sensor.morrisons_fuel_raw" 
echo "  • sensor.sainsburys_fuel_raw"
echo "  • sensor.asda_selected_station_by_home"
echo "  • sensor.morrisons_selected_station_by_home"
echo "  • sensor.sainsburys_selected_station_by_home"
echo "  • sensor.asda_diesel_b7_home"
echo "  • sensor.morrisons_diesel_b7_home"
echo "  • sensor.sainsburys_diesel_b7_home"
echo "  • sensor.average_local_diesel_price"
echo "  • sensor.heating_oil_cost_per_kwh"

echo ""
echo "🚀 Next steps:"
echo "1. Restart Home Assistant"
echo "2. Check Developer Tools → States for new sensors"
echo "3. Look for any remaining template errors in logs"
echo "4. Verify fuel prices are loading (may take up to 1 hour for first data)"

echo ""
echo "✅ Configuration fixed and ready!"