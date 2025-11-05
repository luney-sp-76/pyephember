#!/bin/bash
# Check Home Assistant Climate Entities via REST API
# Usage: ./check_climate_entities.sh [HA_URL] [TOKEN]
# Example: ./check_climate_entities.sh http://homeassistant.local:8123 your_long_lived_token

HA_URL=${1:-"http://homeassistant.local:8123"}
TOKEN=${2:-""}

if [ -z "$TOKEN" ]; then
    echo "Usage: $0 [HA_URL] [TOKEN]"
    echo "Example: $0 http://homeassistant.local:8123 your_long_lived_token"
    echo ""
    echo "To get a token:"
    echo "1. Go to Settings > Security > Long-lived access tokens"
    echo "2. Create a new token"
    echo "3. Use it as the second parameter"
    echo ""
    echo "Default URL is: $HA_URL"
    exit 1
fi

echo "=========================================="
echo "Home Assistant Climate Entity Check"
echo "URL: $HA_URL"
echo "$(date)"
echo "=========================================="

# Test connection first
echo "Testing connection..."
RESPONSE=$(curl -s -w "%{http_code}" -H "Authorization: Bearer $TOKEN" "$HA_URL/api/" -o /dev/null)
if [ "$RESPONSE" != "200" ]; then
    echo "❌ Connection failed (HTTP $RESPONSE)"
    echo "   Check URL and token"
    exit 1
fi
echo "✅ Connection successful"

# Get all climate entities
echo ""
echo "=== ALL CLIMATE ENTITIES ==="
curl -s -H "Authorization: Bearer $TOKEN" \
     "$HA_URL/api/states" | \
     jq -r '.[] | select(.entity_id | startswith("climate.")) | .entity_id' | \
     sort

# Get entities containing "eph" or "ember"
echo ""
echo "=== EPH/EMBER ENTITIES ==="
curl -s -H "Authorization: Bearer $TOKEN" \
     "$HA_URL/api/states" | \
     jq -r '.[] | select(.entity_id | test("eph|ember"; "i")) | .entity_id' | \
     sort

# Check integration status
echo ""
echo "=== INTEGRATION STATUS ==="
echo "Checking for loaded integrations..."
curl -s -H "Authorization: Bearer $TOKEN" \
     "$HA_URL/api/config/integrations" | \
     jq -r '.[] | select(.domain | test("eph|ember"; "i")) | "\(.domain): \(.title)"' || echo "No EPH/Ember integrations found"

echo ""
echo "=========================================="
echo "NEXT STEPS"
echo "=========================================="
echo "1. If you see climate entities above, note their exact names"
echo "2. Update your heating_analytics_package.yaml with the correct entity names"
echo "3. If no climate entities, check Settings > Devices & Services in HA"
echo "4. Look for EPH Controls or similar integration to configure"