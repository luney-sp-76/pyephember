#!/bin/bash
"""
EPH Home Assistant Setup Script
Sets up environment variables and tests the EPH connection
"""

echo "=== EPH Home Assistant Integration Setup ==="
echo

# Check if we're in the right directory
if [ ! -f "enhanced_eph_ember.py" ]; then
    echo "ERROR: Please run this script from the directory containing enhanced_eph_ember.py"
    exit 1
fi

# Check if pyephember2 is installed
echo "Checking pyephember2 installation..."
python3 -c "import pyephember2.pyephember2; print('✓ pyephember2 is installed')" 2>/dev/null || {
    echo "✗ pyephember2 not found. Installing..."
    pip3 install --break-system-packages pyephember2==0.4.12
}

echo
echo "Please enter your EPH Controls credentials:"
echo

# Get credentials from user
read -p "EPH Username: " EPH_USERNAME
read -s -p "EPH Password: " EPH_PASSWORD
echo

# Export environment variables
export EPH_USERNAME="$EPH_USERNAME"
export EPH_PASSWORD="$EPH_PASSWORD"

echo
echo "Credentials set. Testing connection..."
echo

# Test the connection
python3 test_eph_connection.py

if [ $? -eq 0 ]; then
    echo
    echo "=== SUCCESS! ==="
    echo "Your EPH integration is working. You can now use:"
    echo
    echo "export EPH_USERNAME='$EPH_USERNAME'"
    echo "export EPH_PASSWORD='$EPH_PASSWORD'"
    echo "python3 enhanced_eph_ember.py status"
    echo
    echo "Or add these to your ~/.bashrc or ~/.zshrc:"
    echo "echo 'export EPH_USERNAME=\"$EPH_USERNAME\"' >> ~/.zshrc"
    echo "echo 'export EPH_PASSWORD=\"$EPH_PASSWORD\"' >> ~/.zshrc"
    echo
else
    echo
    echo "=== CONNECTION FAILED ==="
    echo "Please check your credentials and try again."
    echo
fi