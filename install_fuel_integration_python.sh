#!/bin/bash
# Installation script for Python-based fuel price integration

set -e

echo "🚗 Installing Python-based Fuel Price Integration"
echo "================================================="

# Check if we're running as root or have sudo access
if [[ $EUID -eq 0 ]]; then
    echo "✓ Running as root"
    SUDO=""
elif sudo -n true 2>/dev/null; then
    echo "✓ Sudo access available"
    SUDO="sudo"
else
    echo "❌ This script requires root access or sudo privileges"
    echo "Please run as root or ensure sudo is available"
    exit 1
fi

# Check if running on Home Assistant OS
if [ -d "/usr/share/hassio" ] || [ -f "/etc/hassio.json" ]; then
    echo "✓ Detected Home Assistant OS"
    SCRIPT_DIR="/config/scripts"
    CONFIG_DIR="/config"
else
    echo "✓ Detected standard Linux/macOS system"
    SCRIPT_DIR="/usr/local/bin"
    CONFIG_DIR="."
fi

echo "Script directory: $SCRIPT_DIR"
echo "Config directory: $CONFIG_DIR"

# Create script directory if it doesn't exist
$SUDO mkdir -p "$SCRIPT_DIR"

# Copy the Python scripts
echo "📁 Installing Python scripts..."
$SUDO cp fuel_price_analyzer.py "$SCRIPT_DIR/"
$SUDO cp ha_fuel_prices.py "$SCRIPT_DIR/"

# Make scripts executable
$SUDO chmod +x "$SCRIPT_DIR/fuel_price_analyzer.py"
$SUDO chmod +x "$SCRIPT_DIR/ha_fuel_prices.py"

# Copy configuration template
echo "📋 Installing configuration template..."
if [ "$CONFIG_DIR" != "." ]; then
    cp fuel_price_ha_config.yaml "$CONFIG_DIR/packages/fuel_prices.yaml" 2>/dev/null || {
        echo "⚠️  Could not install to packages directory"
        echo "   Please manually copy fuel_price_ha_config.yaml to your packages directory"
    }
fi

# Test the installation
echo "🧪 Testing installation..."
if python3 "$SCRIPT_DIR/ha_fuel_prices.py" test_api; then
    echo "✅ Installation successful!"
else
    echo "⚠️  Installation completed but API test failed"
    echo "   This might be due to network connectivity or API changes"
fi

echo ""
echo "📖 Next steps:"
echo "1. Copy fuel_price_ha_config.yaml to your Home Assistant packages directory"
echo "2. Update the home_postcode input_text with your actual postcode"
echo "3. Restart Home Assistant"
echo "4. Check that the new fuel price sensors appear in Home Assistant"
echo ""
echo "🔧 Manual testing:"
echo "   $SCRIPT_DIR/ha_fuel_prices.py get_cheapest YourPostcode"
echo "   $SCRIPT_DIR/fuel_price_analyzer.py YourPostcode"
echo ""
echo "📁 Files installed:"
echo "   $SCRIPT_DIR/fuel_price_analyzer.py"
echo "   $SCRIPT_DIR/ha_fuel_prices.py"
if [ "$CONFIG_DIR" != "." ]; then
    echo "   $CONFIG_DIR/packages/fuel_prices.yaml (if packages directory exists)"
fi