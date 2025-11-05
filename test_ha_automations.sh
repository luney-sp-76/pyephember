#!/usr/bin/env bash
# Home Assistant Heating & Humidity Test Script
# Run this via SSH: bash /config/scripts/test_automations.sh

echo "🧪 Home Assistant Heating & Humidity Test Suite"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to test HA CLI availability
test_ha_cli() {
    echo -e "\n${BLUE}🔧 Testing Home Assistant CLI...${NC}"
    if command -v ha &> /dev/null; then
        echo -e "${GREEN}✅ HA CLI available${NC}"
        ha --version
        return 0
    else
        echo -e "${YELLOW}⚠️  HA CLI not available, using alternative methods${NC}"
        return 1
    fi
}

# Function to test core services
test_core_services() {
    echo -e "\n${BLUE}🏠 Testing Core Services...${NC}"
    
    # Check if Home Assistant is running
    if pgrep -f "homeassistant" > /dev/null; then
        echo -e "${GREEN}✅ Home Assistant process running${NC}"
    else
        echo -e "${RED}❌ Home Assistant process not found${NC}"
        return 1
    fi
    
    # Check configuration files
    if [ -f "/config/configuration.yaml" ]; then
        echo -e "${GREEN}✅ Configuration file exists${NC}"
    else
        echo -e "${RED}❌ Configuration file missing${NC}"
        return 1
    fi
    
    return 0
}

# Function to check EPH Ember integration
test_eph_ember() {
    echo -e "\n${BLUE}🔥 Testing EPH Ember Integration...${NC}"
    
    # Check if EPH Ember script exists
    if [ -f "/config/scripts/eph_ember.py" ]; then
        echo -e "${GREEN}✅ EPH Ember script found${NC}"
        
        # Test if Python and pyephember are available
        if python3 -c "import pyephember" 2>/dev/null; then
            echo -e "${GREEN}✅ PyEphEmber library available${NC}"
            
            # Test script functionality (if credentials are set)
            if [ -n "$EPH_EMAIL" ] && [ -n "$EPH_PASSWORD" ]; then
                echo -e "${BLUE}🔧 Testing zone listing...${NC}"
                cd /config/scripts
                if python3 eph_ember.py list_zones 2>/dev/null; then
                    echo -e "${GREEN}✅ EPH Ember zones accessible${NC}"
                else
                    echo -e "${YELLOW}⚠️  EPH Ember connection failed (check credentials)${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  EPH credentials not set (EPH_EMAIL, EPH_PASSWORD)${NC}"
            fi
        else
            echo -e "${RED}❌ PyEphEmber library not installed${NC}"
            echo "   Run: pip install pyephember"
        fi
    else
        echo -e "${YELLOW}⚠️  EPH Ember script not found at /config/scripts/eph_ember.py${NC}"
    fi
}

# Function to check automations
test_automations() {
    echo -e "\n${BLUE}🤖 Testing Automations...${NC}"
    
    if [ -f "/config/automations.yaml" ]; then
        echo -e "${GREEN}✅ Automations file exists${NC}"
        
        # Count automations
        automation_count=$(grep -c "^- alias:" /config/automations.yaml 2>/dev/null || echo "0")
        echo -e "${BLUE}📊 Found $automation_count automations${NC}"
        
        # Look for heating-related automations
        heating_automations=$(grep -i -E "(heat|temp|climate|warm|cold)" /config/automations.yaml | wc -l)
        echo -e "${BLUE}🔥 $heating_automations heating-related automation entries${NC}"
        
        # Look for humidity-related automations  
        humidity_automations=$(grep -i -E "(humid|moisture|dry)" /config/automations.yaml | wc -l)
        echo -e "${BLUE}💧 $humidity_automations humidity-related automation entries${NC}"
        
    else
        echo -e "${YELLOW}⚠️  No automations.yaml file found${NC}"
    fi
    
    # Check for automation files in automations/
    if [ -d "/config/automations" ]; then
        auto_files=$(find /config/automations -name "*.yaml" | wc -l)
        echo -e "${BLUE}📁 $auto_files automation files in /config/automations/${NC}"
    fi
}

# Function to check sensors and climate entities
test_climate_config() {
    echo -e "\n${BLUE}🌡️  Testing Climate Configuration...${NC}"
    
    # Check for climate platform configurations
    if grep -q "climate:" /config/configuration.yaml 2>/dev/null; then
        echo -e "${GREEN}✅ Climate platform configured${NC}"
    else
        echo -e "${YELLOW}⚠️  No climate platform found in configuration.yaml${NC}"
    fi
    
    # Check for EPH Ember integration in config
    if grep -i -q "eph" /config/configuration.yaml 2>/dev/null; then
        echo -e "${GREEN}✅ EPH Ember mentioned in configuration${NC}"
    fi
    
    # Look for template sensors
    if grep -q "template:" /config/configuration.yaml 2>/dev/null; then
        echo -e "${GREEN}✅ Template sensors configured${NC}"
    fi
    
    # Check for custom integrations
    if [ -d "/config/custom_components" ]; then
        custom_integrations=$(ls /config/custom_components | wc -l)
        echo -e "${BLUE}🔌 $custom_integrations custom integrations installed${NC}"
        
        if [ -d "/config/custom_components/eph_ember" ]; then
            echo -e "${GREEN}✅ EPH Ember custom integration found${NC}"
        fi
    fi
}

# Function to test log files for errors
test_logs() {
    echo -e "\n${BLUE}📝 Checking Recent Logs...${NC}"
    
    if [ -f "/config/home-assistant.log" ]; then
        echo -e "${GREEN}✅ Home Assistant log file exists${NC}"
        
        # Check for recent errors
        error_count=$(tail -100 /config/home-assistant.log | grep -i "error" | wc -l)
        warning_count=$(tail -100 /config/home-assistant.log | grep -i "warning" | wc -l)
        
        echo -e "${BLUE}📊 Recent log summary (last 100 lines):${NC}"
        echo -e "   Errors: $error_count"
        echo -e "   Warnings: $warning_count"
        
        # Check for EPH-related log entries
        eph_logs=$(tail -100 /config/home-assistant.log | grep -i "eph" | wc -l)
        if [ "$eph_logs" -gt 0 ]; then
            echo -e "${BLUE}🔥 $eph_logs EPH-related log entries found${NC}"
            echo -e "${BLUE}Recent EPH logs:${NC}"
            tail -100 /config/home-assistant.log | grep -i "eph" | tail -3
        fi
    else
        echo -e "${YELLOW}⚠️  Home Assistant log file not found${NC}"
    fi
}

# Function to test network connectivity
test_connectivity() {
    echo -e "\n${BLUE}🌐 Testing Network Connectivity...${NC}"
    
    # Test internet connectivity
    if ping -c 1 8.8.8.8 &> /dev/null; then
        echo -e "${GREEN}✅ Internet connectivity working${NC}"
    else
        echo -e "${RED}❌ No internet connectivity${NC}"
    fi
    
    # Test EPH Ember API endpoint
    if command -v curl &> /dev/null; then
        if curl -s --connect-timeout 5 https://eu-https.topband-cloud.com > /dev/null; then
            echo -e "${GREEN}✅ EPH Ember API endpoint reachable${NC}"
        else
            echo -e "${RED}❌ EPH Ember API endpoint unreachable${NC}"
        fi
    fi
}

# Function to create test summary
create_summary() {
    echo -e "\n${BLUE}=============================================="
    echo -e "📊 TEST SUMMARY"
    echo -e "==============================================${NC}"
    
    echo -e "${GREEN}✅ Completed tests:${NC}"
    echo -e "   • Core services status"
    echo -e "   • EPH Ember integration"
    echo -e "   • Automation configuration"
    echo -e "   • Climate entity setup"
    echo -e "   • Log file analysis"
    echo -e "   • Network connectivity"
    
    echo -e "\n${BLUE}🚀 Next steps to test live functionality:${NC}"
    echo -e "   1. Check HA web interface: http://$(hostname -I | awk '{print $1}'):8123"
    echo -e "   2. Manually trigger an automation"
    echo -e "   3. Test temperature change via EPH script"
    echo -e "   4. Monitor logs during testing"
    
    echo -e "\n${YELLOW}💡 Quick tests you can run:${NC}"
    echo -e "   • tail -f /config/home-assistant.log"
    echo -e "   • cd /config/scripts && python3 eph_ember.py list_zones"
    echo -e "   • ha automation list (if HA CLI available)"
}

# Main execution
main() {
    test_ha_cli
    test_core_services
    test_eph_ember
    test_automations
    test_climate_config
    test_logs
    test_connectivity
    create_summary
    
    echo -e "\n${GREEN}🎉 Heating & Humidity test suite completed!${NC}"
}

# Run the main function
main