#!/usr/bin/env python3
"""
Home Assistant Fuel Price Command Line Integration
Provides command line interface for Home Assistant command_line sensors
Usage similar to eph_ember.py script
"""

import sys
import json
import os
from fuel_price_analyzer import FuelPriceAnalyzer, PostcodeUtils

class HAFuelInterface:
    """Home Assistant command line interface for fuel prices"""
    
    def __init__(self):
        self.analyzer = FuelPriceAnalyzer()
        # Cache file to avoid repeated API calls
        self.cache_file = "/tmp/fuel_prices_cache.json"
        self.cache_duration = 3600  # 1 hour
    
    def get_cached_data(self, postcode: str):
        """Get cached fuel data if still valid"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache = json.load(f)
                
                # Check if cache is still valid and for the right postcode
                import time
                if (cache.get('timestamp', 0) + self.cache_duration > time.time() and
                    cache.get('postcode', '').upper() == postcode.upper()):
                    return cache.get('data')
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            pass
        return None
    
    def cache_data(self, postcode: str, data: dict):
        """Cache fuel data to avoid repeated API calls"""
        try:
            import time
            cache = {
                'timestamp': time.time(),
                'postcode': postcode.upper(),
                'data': data
            }
            with open(self.cache_file, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            # Don't fail if caching fails
            print(f"Warning: Could not cache data: {e}", file=sys.stderr)
    
    def get_fuel_data(self, postcode: str):
        """Get fuel data for postcode, using cache if available"""
        # Try cache first
        cached = self.get_cached_data(postcode)
        if cached:
            return cached
        
        # Fetch fresh data
        data = self.analyzer.get_diesel_prices_summary(postcode)
        self.cache_data(postcode, data)
        return data
    
    def get_diesel_price(self, brand: str, postcode: str) -> str:
        """Get diesel price for specific brand near postcode"""
        try:
            data = self.get_fuel_data(postcode)
            brand_upper = brand.upper()
            
            # Try exact brand match first
            for key, value in data.items():
                if key.upper() == brand_upper:
                    price = value.get('diesel_price_per_litre')
                    return f"{price:.3f}" if price else "unavailable"
            
            # Try partial match
            for key, value in data.items():
                if brand_upper in key.upper():
                    price = value.get('diesel_price_per_litre')
                    return f"{price:.3f}" if price else "unavailable"
            
            return "unknown_brand"
            
        except Exception as e:
            print(f"Error getting diesel price: {e}", file=sys.stderr)
            return "error"
    
    def get_station_info(self, brand: str, postcode: str) -> str:
        """Get station information for specific brand near postcode"""
        try:
            data = self.get_fuel_data(postcode)
            brand_upper = brand.upper()
            
            for key, value in data.items():
                if brand_upper in key.upper():
                    return json.dumps({
                        'station_id': value.get('station_id'),
                        'name': value.get('station_name'),
                        'postcode': value.get('postcode'),
                        'diesel_price': value.get('diesel_price_per_litre')
                    })
            
            return json.dumps({'error': 'brand_not_found'})
            
        except Exception as e:
            print(f"Error getting station info: {e}", file=sys.stderr)
            return json.dumps({'error': 'api_error'})
    
    def get_cheapest_diesel(self, postcode: str) -> str:
        """Get the cheapest diesel price near postcode"""
        try:
            data = self.get_fuel_data(postcode)
            
            cheapest_price = None
            cheapest_brand = None
            
            for brand, info in data.items():
                price = info.get('diesel_price_per_litre')
                if price and (cheapest_price is None or price < cheapest_price):
                    cheapest_price = price
                    cheapest_brand = brand
            
            if cheapest_price:
                return f"{cheapest_price:.3f}"
            return "no_prices"
            
        except Exception as e:
            print(f"Error getting cheapest price: {e}", file=sys.stderr)
            return "error"
    
    def get_price_comparison(self, postcode: str) -> str:
        """Get price comparison as JSON string"""
        try:
            data = self.get_fuel_data(postcode)
            
            comparison = {}
            for brand, info in data.items():
                price = info.get('diesel_price_per_litre')
                if price:
                    comparison[brand] = {
                        'price_per_litre': price,
                        'price_per_kwh': price / 10,  # ~10 kWh per litre
                        'station': info.get('station_name'),
                        'postcode': info.get('postcode')
                    }
            
            return json.dumps(comparison)
            
        except Exception as e:
            print(f"Error getting price comparison: {e}", file=sys.stderr)
            return json.dumps({'error': 'api_error'})

def usage():
    """Print usage information"""
    print("""
Usage: ha_fuel_prices.py <command> [brand] [postcode]

Commands:
  get_diesel <brand> <postcode>    - Get diesel price for brand near postcode
  get_station <brand> <postcode>   - Get station info for brand near postcode
  get_cheapest <postcode>          - Get cheapest diesel price near postcode
  get_comparison <postcode>        - Get price comparison JSON
  test_api                         - Test API connectivity

Brands: ASDA, Sainsburys, Tesco

Examples:
  ha_fuel_prices.py get_diesel ASDA BT8
  ha_fuel_prices.py get_cheapest "BT8 8FD"
  ha_fuel_prices.py get_comparison BT8
""")

def main():
    """Main command line interface"""
    if len(sys.argv) < 2:
        usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    interface = HAFuelInterface()
    
    try:
        if command == "get_diesel":
            if len(sys.argv) != 4:
                print("Usage: get_diesel <brand> <postcode>", file=sys.stderr)
                sys.exit(1)
            brand = sys.argv[2]
            postcode = sys.argv[3]
            result = interface.get_diesel_price(brand, postcode)
            print(result)
        
        elif command == "get_station":
            if len(sys.argv) != 4:
                print("Usage: get_station <brand> <postcode>", file=sys.stderr)
                sys.exit(1)
            brand = sys.argv[2]
            postcode = sys.argv[3]
            result = interface.get_station_info(brand, postcode)
            print(result)
        
        elif command == "get_cheapest":
            if len(sys.argv) != 3:
                print("Usage: get_cheapest <postcode>", file=sys.stderr)
                sys.exit(1)
            postcode = sys.argv[2]
            result = interface.get_cheapest_diesel(postcode)
            print(result)
        
        elif command == "get_comparison":
            if len(sys.argv) != 3:
                print("Usage: get_comparison <postcode>", file=sys.stderr)
                sys.exit(1)
            postcode = sys.argv[2]
            result = interface.get_price_comparison(postcode)
            print(result)
        
        elif command == "test_api":
            # Test with a known postcode
            test_postcode = "BT8"
            print(f"Testing API with postcode: {test_postcode}")
            data = interface.get_fuel_data(test_postcode)
            print(f"Found data for {len(data)} brands")
            for brand in data.keys():
                print(f"  {brand}: OK")
        
        else:
            print(f"Unknown command: {command}", file=sys.stderr)
            usage()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()