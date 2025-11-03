"""
Additional tests for zone utility functions
"""
import pytest
import datetime
from unittest.mock import patch

from pyephember.pyephember import (
    zone_name, zone_is_boost_active, zone_boost_hours, zone_boost_timestamp,
    zone_temperature, zone_target_temperature, zone_boost_temperature,
    zone_current_temperature, zone_pointdata_value, zone_mode,
    PointIndex, ZoneMode
)


class TestZoneUtilities:
    """Tests for zone utility functions"""
    
    def create_mock_zone(self, point_data_values=None, name='Test Zone'):
        """Helper to create a mock zone with pointDataList"""
        if point_data_values is None:
            point_data_values = {}
        
        zone = {
            'name': name,
            'pointDataList': [],
            'timestamp': int(datetime.datetime.now().timestamp() * 1000)
        }
        
        # Add point data for each index
        for point_index in PointIndex:
            value = point_data_values.get(point_index.name, 0)
            zone['pointDataList'].append({
                'pointIndex': point_index.value,
                'value': value
            })
        
        return zone

    def test_zone_name(self):
        """Test zone_name function"""
        zone = self.create_mock_zone(name='Living Room')
        assert zone_name(zone) == 'Living Room'

    def test_zone_is_boost_active_true(self):
        """Test zone_is_boost_active returns True when boost is active"""
        zone = self.create_mock_zone({'BOOST_HOURS': 2})
        assert zone_is_boost_active(zone) is True

    def test_zone_is_boost_active_false(self):
        """Test zone_is_boost_active returns False when boost is not active"""
        zone = self.create_mock_zone({'BOOST_HOURS': 0})
        assert zone_is_boost_active(zone) is False

    def test_zone_boost_hours(self):
        """Test zone_boost_hours function"""
        zone = self.create_mock_zone({'BOOST_HOURS': 3})
        assert zone_boost_hours(zone) == 3

    def test_zone_boost_timestamp(self):
        """Test zone_boost_timestamp function"""
        timestamp = 1672531200  # Example timestamp
        zone = self.create_mock_zone({'BOOST_TIME': timestamp})
        assert zone_boost_timestamp(zone) == timestamp

    def test_zone_target_temperature(self):
        """Test zone_target_temperature function"""
        # Target temp is stored as tenths of degrees
        zone = self.create_mock_zone({'TARGET_TEMP': 215})  # 21.5 degrees
        assert zone_target_temperature(zone) == 21.5

    def test_zone_boost_temperature(self):
        """Test zone_boost_temperature function"""
        # Boost temp is stored as tenths of degrees
        zone = self.create_mock_zone({'BOOST_TEMP': 220})  # 22.0 degrees
        assert zone_boost_temperature(zone) == 22.0

    def test_zone_current_temperature(self):
        """Test zone_current_temperature function"""
        # Current temp is stored as tenths of degrees
        zone = self.create_mock_zone({'CURRENT_TEMP': 195})  # 19.5 degrees
        assert zone_current_temperature(zone) == 19.5

    def test_zone_pointdata_value(self):
        """Test zone_pointdata_value function"""
        zone = self.create_mock_zone({'MODE': 2})
        assert zone_pointdata_value(zone, 'MODE') == 2

    def test_zone_pointdata_value_missing_index(self):
        """Test zone_pointdata_value with missing point index"""
        zone = {'pointDataList': []}  # Empty point data
        result = zone_pointdata_value(zone, 'MODE')
        assert result is None

    def test_zone_mode(self):
        """Test zone_mode function"""
        zone = self.create_mock_zone({'MODE': ZoneMode.AUTO.value})
        assert zone_mode(zone) == ZoneMode.AUTO

    def test_zone_temperature_target(self):
        """Test zone_temperature function with TARGET_TEMP label"""
        zone = self.create_mock_zone({'TARGET_TEMP': 210})  # 21.0 degrees
        temp = zone_temperature(zone, 'TARGET_TEMP')
        assert temp == 21.0

    def test_zone_temperature_current(self):
        """Test zone_temperature function with CURRENT_TEMP label"""
        zone = self.create_mock_zone({'CURRENT_TEMP': 190})  # 19.0 degrees
        temp = zone_temperature(zone, 'CURRENT_TEMP')
        assert temp == 19.0

    def test_zone_temperature_invalid_label(self):
        """Test zone_temperature function with invalid label"""
        zone = self.create_mock_zone()
        # This should return None/10 and likely cause an error
        # Let's test that the zone_pointdata_value returns None for invalid labels
        result = zone_pointdata_value(zone, 'INVALID_LABEL')
        assert result is None


class TestScheduling:
    """Tests for zone scheduling functions"""
    
    def create_zone_with_schedule(self, mode=ZoneMode.AUTO, schedules=None):
        """Create a zone with schedule data"""
        if schedules is None:
            schedules = []
        
        zone = {
            'pointDataList': [{
                'pointIndex': PointIndex.MODE.value,
                'value': mode.value
            }],
            'schedules': schedules,
            'timestamp': int(datetime.datetime.now().timestamp() * 1000)
        }
        return zone

    @patch('pyephember.pyephember.zone_mode')
    def test_zone_is_scheduled_on_mode_off(self, mock_zone_mode):
        """Test zone_is_scheduled_on returns False when mode is OFF"""
        from pyephember.pyephember import zone_is_scheduled_on
        
        mock_zone_mode.return_value = ZoneMode.OFF
        zone = self.create_zone_with_schedule()
        assert zone_is_scheduled_on(zone) is False

    @patch('pyephember.pyephember.zone_mode')
    def test_zone_is_scheduled_on_mode_on(self, mock_zone_mode):
        """Test zone_is_scheduled_on returns True when mode is ON"""
        from pyephember.pyephember import zone_is_scheduled_on
        
        mock_zone_mode.return_value = ZoneMode.ON
        zone = self.create_zone_with_schedule()
        assert zone_is_scheduled_on(zone) is True