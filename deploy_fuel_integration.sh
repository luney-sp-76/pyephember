#!/bin/bash
# Fuel Cost Integration Deployment Script
# Copy this to your Home Assistant host and run

echo "🏠 Deploying Fuel Cost Integration to Home Assistant"
echo "================================================="

# Configuration
HA_CONFIG_DIR="/root/config"
PACKAGES_DIR="$HA_CONFIG_DIR/packages" 
LOVELACE_DIR="$HA_CONFIG_DIR/lovelace"

# Create directories if they don't exist
echo "📁 Setting up directories..."
mkdir -p "$PACKAGES_DIR"
mkdir -p "$LOVELACE_DIR"

# Copy package files (working APIs only)
echo "📦 Copying package files..."
if [ -f "fuel_by_home_postcode_working_fixed.yaml" ]; then
    cp fuel_by_home_postcode_working_fixed.yaml "$PACKAGES_DIR/fuel_by_home_postcode.yaml"
    echo "  ✓ fuel_by_home_postcode_working_fixed.yaml → fuel_by_home_postcode.yaml"
else
    echo "  ⚠ fuel_by_home_postcode_working_fixed.yaml not found"
fi

if [ -f "heating_cost_analysis_working.yaml" ]; then
    cp heating_cost_analysis_working.yaml "$PACKAGES_DIR/heating_cost_analysis.yaml"
    echo "  ✓ heating_cost_analysis_working.yaml → heating_cost_analysis.yaml"
else
    echo "  ⚠ heating_cost_analysis_working.yaml not found"
fi

# Copy dashboard
echo "📊 Copying dashboard..."
if [ -f "heating_cost_dashboard.yaml" ]; then
    cp heating_cost_dashboard.yaml "$LOVELACE_DIR/"
    echo "  ✓ heating_cost_dashboard.yaml"
else
    echo "  ⚠ heating_cost_dashboard.yaml not found"
fi

# Verify Home Assistant packages configuration
echo "⚙️ Checking configuration..."
if grep -q "packages:" "$HA_CONFIG_DIR/configuration.yaml"; then
    echo "  ✓ Packages already enabled in configuration.yaml"
else
    echo "  ⚠ Add this to configuration.yaml:"
    echo "    homeassistant:"
    echo "      packages: !include_dir_named packages"
fi

# Check zone.home
echo "📍 Location setup..."
if grep -q "zone.home" "$HA_CONFIG_DIR"/*.yaml "$HA_CONFIG_DIR"/packages/*.yaml 2>/dev/null; then
    echo "  ✓ zone.home appears to be configured"
else
    echo "  ⚠ Ensure zone.home is configured with correct coordinates"
    echo "    Example:"
    echo "    zone:"
    echo "      - name: Home"
    echo "        latitude: 51.5074"
    echo "        longitude: -0.1278"
    echo "        radius: 100"
fi

echo ""
echo "🚀 Next Steps:"
echo "1. Restart Home Assistant"
echo "2. Go to Developer Tools → States"
echo "3. Look for new sensors starting with:"
echo "   • sensor.home_postcode_lookup"
echo "   • sensor.average_local_diesel_price"
echo "   • sensor.heating_oil_cost_per_kwh"
echo "4. Add heating cost dashboard to Lovelace"
echo "5. Monitor for any errors in Home Assistant logs"

echo ""
echo "🎯 Expected Results:"
echo "• Real-time fuel prices from 3 working UK providers (ASDA, Morrisons, Sainsbury's)"
echo "• Cost per kWh for heating oil equivalent"
echo '• Daily heating cost estimates (e.g., "£8.50/day")'
echo "• Integration with existing EPH heating analytics"
echo "• Alerts for high costs or price spikes"

echo ""
echo "✅ Deployment Complete!"