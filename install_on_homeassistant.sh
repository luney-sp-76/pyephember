#!/bin/bash
# EPH Helper Installation Script for Home Assistant

set -e

echo "=== EPH Helper Installation Script ==="
echo ""

# Check if we're on Home Assistant system
if [[ ! -d "/root/config" ]]; then
    echo "❌ This script should be run on your Home Assistant system"
    echo "Please run this on your Home Assistant host, not locally"
    exit 1
fi

# Create scripts directory if it doesn't exist
echo "📁 Creating scripts directory..."
mkdir -p /root/config/scripts

# Check if pyephember2 is installed
echo "🔍 Checking pyephember2 installation..."
if ! python3 -c "import pyephember2.pyephember2" 2>/dev/null; then
    echo "📦 Installing pyephember2..."
    pip3 install --break-system-packages pyephember2==0.4.12
else
    echo "✅ pyephember2 already installed"
fi

# Copy helper script (assuming it's already copied to the system)
if [[ ! -f "/root/config/scripts/eph_helper.py" ]]; then
    echo "❌ eph_helper.py not found in /root/config/scripts/"
    echo "Please copy eph_helper.py to /root/config/scripts/ first"
    exit 1
fi

# Make script executable
chmod +x /root/config/scripts/eph_helper.py

# Create environment file template
echo "📝 Creating environment file template..."
cat > /root/config/scripts/.env << 'EOF'
# EPH Controls Credentials
# Replace with your actual EPH username and password
export EPH_USERNAME="your_eph_username_here"
export EPH_PASSWORD="your_eph_password_here"
EOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "1. Edit /root/config/scripts/.env with your EPH credentials"
echo "2. Test the script: source /root/config/scripts/.env && python3 /root/config/scripts/eph_helper.py zones"
echo "3. Add the sensor configurations to your configuration.yaml"
echo "4. Restart Home Assistant"
echo ""
echo "📖 See SETUP_INSTRUCTIONS.md for complete configuration examples"