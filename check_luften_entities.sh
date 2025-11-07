#!/bin/bash

# Script to discover all entities with "luften" in their name and check availability
# Usage: ./check_luften_entities.sh [HA_HOST] [HA_TOKEN]

HA_HOST=${1:-"192.168.4.159:8123"}
HA_TOKEN=${2:-"YOUR_LONG_LIVED_ACCESS_TOKEN"}

echo "🔍 Discovering entities with 'luften' in their name..."
echo "=================================================="

# Get all states and filter for entities containing "luften" (case-insensitive)
curl -s -X GET \
  "http://${HA_HOST}/api/states" \
  -H "Authorization: Bearer ${HA_TOKEN}" \
  -H "Content-Type: application/json" | \
  jq -r '.[] | select(.entity_id | test("luften"; "i")) | 
    "\(.entity_id): \(.state) (available: \(if .state == "unavailable" or .state == "unknown" then "❌ NO" else "✅ YES" end))"' 2>/dev/null

# If jq fails, try with python
if [ $? -ne 0 ]; then
    echo "Using Python fallback..."
    curl -s -X GET \
      "http://${HA_HOST}/api/states" \
      -H "Authorization: Bearer ${HA_TOKEN}" \
      -H "Content-Type: application/json" | \
      python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    luften_entities = [e for e in data if 'luften' in e['entity_id'].lower()]
    if luften_entities:
        for entity in luften_entities:
            state = entity['state']
            available = '✅ YES' if state not in ['unavailable', 'unknown'] else '❌ NO'
            print(f\"{entity['entity_id']}: {state} (available: {available})\")
    else:
        print('No entities found with \"luften\" in their name')
except Exception as e:
    print(f'Error: {e}')
"
fi

echo ""
echo "📋 Summary:"
echo "- Check entity availability in Home Assistant"
echo "- Entities showing 'unavailable' or 'unknown' need attention"
echo "- You may need to update the HA_TOKEN in this script"