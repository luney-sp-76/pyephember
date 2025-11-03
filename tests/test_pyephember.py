"""
Unit tests for pyephember module
"""
import json
import pytest
import datetime
from unittest.mock import Mock, patch, MagicMock
import requests

from pyephember.pyephember import (
    EphEmber, ZoneMode, PointIndex, ZoneCommand,
    zone_command_to_ints, zone_is_active, zone_advance_active,
    boiler_state, zone_is_scheduled_on
)


class TestZoneCommand:
    """Tests for ZoneCommand namedtuple and related functions"""
    
    def test_zone_command_creation(self):
        """Test that ZoneCommand can be created with name and value"""
        cmd = ZoneCommand('TARGET_TEMP', 21.5)
        assert cmd.name == 'TARGET_TEMP'
        assert cmd.value == 21.5

    def test_zone_command_to_ints_target_temp(self):
        """Test converting TARGET_TEMP command to integers"""
        cmd = ZoneCommand('TARGET_TEMP', 21.5)
        result = zone_command_to_ints(cmd)
        expected = [0, PointIndex.TARGET_TEMP.value, 4, 0, 215]  # 21.5 * 10 = 215
        assert result == expected

    def test_zone_command_to_ints_mode(self):
        """Test converting MODE command to integers"""
        cmd = ZoneCommand('MODE', 1)
        result = zone_command_to_ints(cmd)
        expected = [0, PointIndex.MODE.value, 1, 1]
        assert result == expected

    def test_zone_command_to_ints_invalid_command(self):
        """Test that invalid command raises ValueError"""
        cmd = ZoneCommand('CURRENT_TEMP', 20.0)  # Read-only value
        with pytest.raises(ValueError, match="Cannot write to read-only value"):
            zone_command_to_ints(cmd)

    def test_zone_command_to_ints_datetime(self):
        """Test converting BOOST_TIME with datetime to integers"""
        dt = datetime.datetime(2023, 1, 1, 12, 0, 0)
        cmd = ZoneCommand('BOOST_TIME', dt)
        result = zone_command_to_ints(cmd)
        timestamp = int(dt.timestamp())
        expected = [0, PointIndex.BOOST_TIME.value, 5] + list(timestamp.to_bytes(4, 'big'))
        assert result == expected


class TestZoneUtilityFunctions:
    """Tests for zone utility functions"""
    
    def create_mock_zone(self, point_data_values=None):
        """Helper to create a mock zone with pointDataList"""
        if point_data_values is None:
            point_data_values = {}
        
        zone = {
            'pointDataList': [],
            'timestamp': int(datetime.datetime.now().timestamp() * 1000)
        }
        
        # Add default point data
        for point_index in PointIndex:
            value = point_data_values.get(point_index.name, 0)
            zone['pointDataList'].append({
                'pointIndex': point_index.value,
                'value': value
            })
        
        return zone

    def test_zone_advance_active_true(self):
        """Test zone_advance_active returns True when advance is active"""
        zone = self.create_mock_zone({'ADVANCE_ACTIVE': 1})
        assert zone_advance_active(zone) is True

    def test_zone_advance_active_false(self):
        """Test zone_advance_active returns False when advance is not active"""
        zone = self.create_mock_zone({'ADVANCE_ACTIVE': 0})
        assert zone_advance_active(zone) is False

    def test_boiler_state(self):
        """Test boiler_state returns correct value"""
        zone = self.create_mock_zone({'BOILER_STATE': 2})
        assert boiler_state(zone) == 2

    @patch('pyephember.pyephember.zone_is_scheduled_on')
    def test_zone_is_active_scheduled_on(self, mock_scheduled):
        """Test zone_is_active when zone is scheduled on"""
        mock_scheduled.return_value = True
        zone = self.create_mock_zone()
        assert zone_is_active(zone) is True

    @patch('pyephember.pyephember.zone_is_scheduled_on')
    def test_zone_is_active_boost_hours(self, mock_scheduled):
        """Test zone_is_active when boost hours > 0"""
        mock_scheduled.return_value = False
        zone = self.create_mock_zone({'BOOST_HOURS': 2})
        assert zone_is_active(zone) is True

    @patch('pyephember.pyephember.zone_is_scheduled_on')
    def test_zone_is_active_advance_active(self, mock_scheduled):
        """Test zone_is_active when advance is active"""
        mock_scheduled.return_value = False
        zone = self.create_mock_zone({'ADVANCE_ACTIVE': 1})
        assert zone_is_active(zone) is True


class TestEphEmber:
    """Tests for EphEmber class"""
    
    @patch('pyephember.pyephember.EphEmber._login')
    def test_init_success(self, mock_login):
        """Test successful initialization"""
        mock_login.return_value = True
        
        ember = EphEmber('test@example.com', 'password')
        
        assert ember._user['username'] == 'test@example.com'
        assert ember._user['password'] == 'password'
        assert ember.http_api_base == 'https://eu-https.topband-cloud.com/ember-back/'
        mock_login.assert_called_once()

    @patch('pyephember.pyephember.EphEmber._login')
    def test_init_login_failure(self, mock_login):
        """Test initialization with login failure"""
        mock_login.return_value = False
        
        with pytest.raises(RuntimeError, match="Unable to login"):
            EphEmber('test@example.com', 'wrong_password')

    def test_init_cache_home_not_implemented(self):
        """Test that cache_home raises NotImplementedError"""
        with pytest.raises(RuntimeError, match="cache_home not implemented"):
            EphEmber('test@example.com', 'password', cache_home=True)

    @patch('pyephember.pyephember.EphEmber._login')
    @patch('pyephember.pyephember.EphEmber._http')
    def test_http_with_token(self, mock_http_method, mock_login):
        """Test _http method with token"""
        mock_login.return_value = True
        mock_response = Mock()
        mock_response.status_code = 200
        mock_http_method.return_value = mock_response
        
        ember = EphEmber('test@example.com', 'password')
        ember._login_data = {"data": {"token": "test_token"}}
        
        with patch('pyephember.pyephember.EphEmber._do_auth', return_value=True):
            with patch('requests.post', return_value=mock_response) as mock_post:
                result = ember._http('/test', send_token=True)
                
                assert result == mock_response
                mock_post.assert_called_once()
                # Check that Authorization header was set
                call_args = mock_post.call_args
                assert call_args[1]['headers']['Authorization'] == 'test_token'

    @patch('pyephember.pyephember.EphEmber._login')
    def test_http_error_response(self, mock_login):
        """Test _http method with error response"""
        mock_login.return_value = True
        mock_response = Mock()
        mock_response.status_code = 404
        
        ember = EphEmber('test@example.com', 'password')
        
        with patch('requests.post', return_value=mock_response):
            with pytest.raises(RuntimeError, match="404 response code"):
                ember._http('/test')

    @patch('pyephember.pyephember.EphEmber._login')
    @patch('pyephember.pyephember.EphEmber.get_home_details')
    def test_get_zones(self, mock_get_home_details, mock_login):
        """Test get_zones method"""
        mock_login.return_value = True
        mock_home_data = {
            'zoneData': [
                {'name': 'Living Room', 'temperature': 21.5},
                {'name': 'Bedroom', 'temperature': 19.0}
            ]
        }
        mock_get_home_details.return_value = mock_home_data
        
        ember = EphEmber('test@example.com', 'password')
        zones = ember.get_zones()
        
        assert zones == mock_home_data['zoneData']

    @patch('pyephember.pyephember.EphEmber._login')
    @patch('pyephember.pyephember.EphEmber.get_zones')
    @patch('pyephember.pyephember.zone_current_temperature')
    def test_get_zone_temperature(self, mock_zone_temp, mock_get_zones, mock_login):
        """Test get_zone_temperature method"""
        mock_login.return_value = True
        mock_zones = [
            {'name': 'Living Room'},
            {'name': 'Bedroom'}
        ]
        mock_get_zones.return_value = mock_zones
        mock_zone_temp.return_value = 21.5
        
        ember = EphEmber('test@example.com', 'password')
        temp = ember.get_zone_temperature('Living Room')
        
        assert temp == 21.5
        mock_zone_temp.assert_called_once_with({'name': 'Living Room'})

    @patch('pyephember.pyephember.EphEmber._login')
    @patch('pyephember.pyephember.EphEmber.get_zones')
    def test_get_zone_temperature_not_found(self, mock_get_zones, mock_login):
        """Test get_zone_temperature with non-existent zone"""
        mock_login.return_value = True
        mock_zones = [{'name': 'Living Room'}]
        mock_get_zones.return_value = mock_zones
        
        ember = EphEmber('test@example.com', 'password')
        
        with pytest.raises(RuntimeError, match="Unknown zone"):
            ember.get_zone_temperature('Nonexistent Room')


class TestEnums:
    """Tests for enum classes"""
    
    def test_zone_mode_enum(self):
        """Test ZoneMode enum values"""
        assert ZoneMode.AUTO.value == 0
        assert ZoneMode.ALL_DAY.value == 1
        assert ZoneMode.ON.value == 2
        assert ZoneMode.OFF.value == 3

    def test_point_index_enum(self):
        """Test PointIndex enum values"""
        assert PointIndex.ADVANCE_ACTIVE.value == 4
        assert PointIndex.CURRENT_TEMP.value == 5
        assert PointIndex.TARGET_TEMP.value == 6
        assert PointIndex.MODE.value == 7


# Integration-style tests (these would require mocking the HTTP API)
class TestIntegration:
    """Integration-style tests with mocked HTTP responses"""
    
    @patch('requests.post')
    def test_login_flow(self, mock_post):
        """Test the login flow with mocked HTTP response"""
        # Mock successful login response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'token': 'test_token',
                'refresh_token': 'refresh_token',
                'user_id': 123
            }
        }
        mock_post.return_value = mock_response
        
        ember = EphEmber('test@example.com', 'password')
        
        # Verify login was called with correct data
        assert mock_post.called
        call_args = mock_post.call_args
        data = json.loads(call_args[1]['data'])
        assert data['user'] == 'test@example.com'
        assert data['password'] == 'password'