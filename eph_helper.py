#!/usr/bin/env python3
"""
EPH Controls Helper Script for Home Assistant
Production-ready script for EPH zone control and monitoring
"""

import sys
import json
import os
from pyephember2.pyephember2 import EphEmber
from typing import Dict, Any, Optional

class EPHHelper:
    """EPH Controls helper for Home Assistant integration"""
    
    def __init__(self, username: str = None, password: str = None):
        """Initialize EPH connection"""
        # Try to load .env file from known locations if environment variables aren't set
        if not os.getenv('EPH_USERNAME') or not os.getenv('EPH_PASSWORD'):
            self._load_env_file()
            
        self.username = username or os.getenv('EPH_USERNAME')
        self.password = password or os.getenv('EPH_PASSWORD')
        
        if not self.username or not self.password:
            raise ValueError("EPH credentials required")
        
        self.eph = EphEmber(self.username, self.password)
        self.zone_mapping = self._build_zone_mapping()
    
    def _load_env_file(self):
        """Load environment variables from .env file"""
        env_paths = [
            '/root/config/scripts/.env',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),
            '.env'
        ]
        
        for env_path in env_paths:
            if os.path.exists(env_path):
                try:
                    with open(env_path, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip().strip('"').strip("'")
                                os.environ[key] = value
                    break
                except Exception:
                    continue
    
    def _build_zone_mapping(self) -> Dict[str, str]:
        """Build mapping between zone names and zone IDs"""
        try:
            homes = self.eph.get_homes()
            mapping = {}
            
            if isinstance(homes, list) and len(homes) > 0:
                home = homes[0]
                if isinstance(home, dict) and 'zones' in home:
                    for zone in home['zones']:
                        if isinstance(zone, dict):
                            name = zone.get('name', 'Unknown')
                            zone_id = zone.get('zoneid')
                            if name and zone_id:
                                mapping[name] = zone_id
            
            return mapping
        except Exception:
            # Fallback to discovered working mapping
            return {"ONE": "0fed0b70485649a3af8c8b0e0a12ce57"}
    
    def _get_zone_id(self, zone_name: str) -> str:
        """Get internal zone ID from display name"""
        return self.zone_mapping.get(zone_name, zone_name)
    
    def get_temperature(self, zone_name: str) -> Optional[float]:
        """Get current temperature for zone"""
        try:
            zone_id = self._get_zone_id(zone_name)
            temp = self.eph.get_zone_temperature(zone_id)
            return float(temp) if temp is not None else None
        except Exception:
            return None
    
    def get_target_temperature(self, zone_name: str) -> Optional[float]:
        """Get target temperature for zone"""
        try:
            zone_id = self._get_zone_id(zone_name)
            temp = self.eph.get_zone_target_temperature(zone_id)
            return float(temp) if temp is not None else None
        except Exception:
            return None
    
    def set_target_temperature(self, zone_name: str, temperature: float) -> bool:
        """Set target temperature for zone"""
        try:
            zone_id = self._get_zone_id(zone_name)
            # Note: Check if pyephember2 has set_zone_target_temperature method
            result = self.eph.set_zone_target_temperature(zone_id, temperature)
            return result is not None
        except Exception:
            return False
    
    def is_zone_active(self, zone_name: str) -> Optional[bool]:
        """Check if zone is actively heating"""
        try:
            zone_id = self._get_zone_id(zone_name)
            return self.eph.is_zone_active(zone_id)
        except Exception:
            return None
    
    def is_boiler_on(self, zone_name: str) -> Optional[bool]:
        """Check if boiler is on for zone"""
        try:
            zone_id = self._get_zone_id(zone_name)
            return self.eph.is_zone_boiler_on(zone_id)
        except Exception:
            return None
    
    def get_zone_status(self, zone_name: str) -> Dict[str, Any]:
        """Get comprehensive zone status"""
        return {
            'zone_name': zone_name,
            'zone_id': self._get_zone_id(zone_name),
            'current_temperature': self.get_temperature(zone_name),
            'target_temperature': self.get_target_temperature(zone_name),
            'is_active': self.is_zone_active(zone_name),
            'boiler_on': self.is_boiler_on(zone_name),
            'available_zones': list(self.zone_mapping.keys())
        }

def main():
    """Command line interface"""
    if len(sys.argv) < 2:
        print("Usage: eph_helper.py <command> [zone_name] [value]")
        print("Commands:")
        print("  temperature <zone_name>           - Get current temperature")
        print("  target <zone_name>                - Get target temperature")
        print("  set_target <zone_name> <temp>     - Set target temperature")
        print("  active <zone_name>                - Check if zone is active")
        print("  boiler <zone_name>                - Check if boiler is on")
        print("  status <zone_name>                - Get full zone status")
        print("  zones                             - List available zones")
        print("\nCredentials: Set EPH_USERNAME and EPH_PASSWORD environment variables")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        helper = EPHHelper()
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if command == "zones":
            zones = list(helper.zone_mapping.keys())
            print(json.dumps(zones))
        
        elif len(sys.argv) < 3:
            print("ERROR: Zone name required", file=sys.stderr)
            sys.exit(1)
        
        else:
            zone_name = sys.argv[2]
            
            if command == "temperature":
                temp = helper.get_temperature(zone_name)
                print(temp if temp is not None else "null")
            
            elif command == "target":
                temp = helper.get_target_temperature(zone_name)
                print(temp if temp is not None else "null")
            
            elif command == "set_target":
                if len(sys.argv) < 4:
                    print("ERROR: Temperature value required", file=sys.stderr)
                    sys.exit(1)
                temp = float(sys.argv[3])
                result = helper.set_target_temperature(zone_name, temp)
                print("success" if result else "failed")
            
            elif command == "active":
                active = helper.is_zone_active(zone_name)
                print(str(active).lower() if active is not None else "null")
            
            elif command == "boiler":
                boiler = helper.is_boiler_on(zone_name)
                print(str(boiler).lower() if boiler is not None else "null")
            
            elif command == "status":
                status = helper.get_zone_status(zone_name)
                print(json.dumps(status, indent=2))
            
            else:
                print(f"ERROR: Unknown command: {command}", file=sys.stderr)
                sys.exit(1)
                
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()