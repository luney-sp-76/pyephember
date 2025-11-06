#!/usr/bin/env python3
"""
Test script to verify fuel price APIs are working
"""

import requests
import json
import sys

def test_fuel_api(name, url):
    """Test a fuel price API"""
    print(f"\n=== Testing {name} ===")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'HomeAssistant/1.0',
            'Accept': 'application/json'
        })
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ JSON response received")
                
                # Look for common fields
                if 'stations' in data:
                    stations = data['stations']
                    print(f"✓ Found {len(stations)} stations")
                    
                    if len(stations) > 0:
                        first_station = stations[0]
                        print(f"✓ Sample station: {first_station.get('brand', 'Unknown')} - {first_station.get('postcode', 'No postcode')}")
                        
                        if 'prices' in first_station:
                            prices = first_station['prices']
                            print(f"✓ Fuel prices available: {list(prices.keys())}")
                        else:
                            print("⚠ No prices found in station data")
                else:
                    print("⚠ No 'stations' field found")
                    print(f"Available fields: {list(data.keys())}")
                
            except json.JSONDecodeError:
                print(f"✗ Invalid JSON response")
                print(f"Response: {response.text[:200]}...")
                
        else:
            print(f"✗ HTTP {response.status_code}: {response.reason}")
            
    except requests.exceptions.Timeout:
        print(f"✗ Request timeout")
    except requests.exceptions.RequestException as e:
        print(f"✗ Request failed: {e}")

def main():
    """Test multiple fuel APIs"""
    apis = [
        ("Tesco", "https://www.tesco.com/fuel_prices/fuel_prices_data.json"),
        ("ASDA", "https://storelocator.asda.com/fuel_prices_data.json"),
        ("BP", "https://www.bp.com/en_gb/united-kingdom/home/fuelprices/fuel_prices_data.json"),
        ("Morrisons", "https://www.morrisons.com/fuel-prices/fuel.json"),
        ("Sainsbury's", "https://api.sainsburys.co.uk/v1/exports/latest/fuel_prices_data.json"),
    ]
    
    print("Testing Fuel Price APIs")
    print("=" * 50)
    
    working_count = 0
    for name, url in apis:
        try:
            test_fuel_api(name, url)
            working_count += 1
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
            break
    
    print(f"\n" + "=" * 50)
    print(f"Summary: {working_count}/{len(apis)} APIs tested")

if __name__ == "__main__":
    main()