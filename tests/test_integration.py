"""
Integration tests that can work with real EPH Ember credentials
Run these tests with real credentials using environment variables
"""
import os
import pytest
from pyephember.pyephember import EphEmber

# Skip integration tests unless explicitly enabled
pytestmark = pytest.mark.skipif(
    not os.environ.get('PYEPHEMBER_INTEGRATION_TESTS'),
    reason="Integration tests require PYEPHEMBER_INTEGRATION_TESTS=1 environment variable"
)


class TestIntegrationWithRealAPI:
    """Integration tests using real EPH Ember API credentials"""
    
    @pytest.fixture
    def credentials(self):
        """Get credentials from environment variables"""
        email = os.environ.get('PYEPHEMBER_EMAIL')
        password = os.environ.get('PYEPHEMBER_PASSWORD') 
        
        if not email or not password:
            pytest.skip("Real credentials required: set PYEPHEMBER_EMAIL and PYEPHEMBER_PASSWORD environment variables")
        
        return email, password
    
    @pytest.fixture
    def ember_client(self, credentials):
        """Create EphEmber client with real credentials"""
        email, password = credentials
        try:
            client = EphEmber(email, password)
            yield client
        except Exception as e:
            pytest.fail(f"Failed to create EphEmber client: {e}")
    
    def test_login_and_get_home(self, ember_client):
        """Test login and fetching home data"""
        home_data = ember_client.get_home()
        
        # Basic validation
        assert isinstance(home_data, dict)
        assert 'name' in home_data or 'zoneData' in home_data
    
    def test_get_zones(self, ember_client):
        """Test fetching zone data"""
        zones = ember_client.get_zones()
        
        # Basic validation
        assert isinstance(zones, list)
        if zones:  # If there are zones
            zone = zones[0]
            assert isinstance(zone, dict)
            assert 'name' in zone
    
    def test_zone_temperature_if_zones_exist(self, ember_client):
        """Test getting zone temperature (only if zones exist)"""
        zones = ember_client.get_zones()
        
        if zones:  # Only test if zones exist
            zone_name = zones[0]['name']
            temp = ember_client.get_zone_temperature(zone_name)
            
            # Temperature should be a reasonable number
            assert isinstance(temp, (int, float))
            assert -10 <= temp <= 50  # Reasonable temperature range