#!/usr/bin/env python3
"""
Fuel Price Analyzer - Python replacement for Home Assistant YAML templates
Fetches fuel prices from multiple APIs and finds stations near a given postcode
"""

import urllib.request
import urllib.error
import ssl
import gzip
import json
import re
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class FuelStation:
    """Represents a fuel station with pricing data"""
    site_id: str
    brand: str
    name: str
    postcode: str
    address: str
    prices: Dict[str, float]
    distance_km: Optional[float] = None
    
    def get_diesel_price(self) -> Optional[float]:
        """Get diesel price in £/L, trying different fuel type keys"""
        fuel_keys = ['B7', 'diesel', 'Diesel', 'DIESEL', 'gasoil', 'gas_oil']
        for key in fuel_keys:
            if key in self.prices and self.prices[key] is not None:
                # Convert from pence to pounds if needed
                price = self.prices[key]
                if price > 10:  # Assume pence if > £10/L
                    return price / 100
                return price
        return None

@dataclass
class PostcodeInfo:
    """Represents postcode information"""
    full_postcode: str
    outcode: str
    area: str

class FuelPriceAPI:
    """Base class for fuel price API implementations"""
    
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive'
        }
    
    def fetch_data(self) -> Optional[Dict]:
        """Fetch raw data from the API"""
        try:
            print(f"Fetching {self.name} fuel data...")
            
            # Create request with headers
            req = urllib.request.Request(self.url, headers=self.headers)
            
            # Create SSL context that's more lenient with certificates
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(req, timeout=30, context=ssl_context) as response:
                if response.getcode() == 200:
                    data = response.read()
                    
                    # Handle gzip compressed responses
                    if response.getheader('Content-Encoding') == 'gzip':
                        data = gzip.decompress(data)
                    
                    # Try to detect gzip even if header missing
                    elif data[:2] == b'\x1f\x8b':
                        try:
                            data = gzip.decompress(data)
                        except:
                            pass  # If decompression fails, use original data
                    
                    text_data = data.decode('utf-8')
                    return json.loads(text_data)
                else:
                    print(f"HTTP {response.getcode()} error fetching {self.name} data")
                    return None
                    
        except urllib.error.HTTPError as e:
            print(f"HTTP Error fetching {self.name} data: {e.code} {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"URL Error fetching {self.name} data: {e.reason}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error parsing {self.name} JSON: {e}")
            return None
        except UnicodeDecodeError as e:
            print(f"Encoding error fetching {self.name} data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error fetching {self.name} data: {e}")
            return None
    
    def parse_stations(self, data: Dict) -> List[FuelStation]:
        """Parse stations from API data - override in subclasses"""
        raise NotImplementedError

class AsdaAPI(FuelPriceAPI):
    """ASDA fuel price API implementation"""
    
    def __init__(self):
        super().__init__("ASDA", "https://storelocator.asda.com/fuel_prices_data.json")
    
    def parse_stations(self, data: Dict) -> List[FuelStation]:
        stations = []
        if 'stations' in data:
            for station_data in data['stations']:
                try:
                    station = FuelStation(
                        site_id=str(station_data.get('site_id', '')),
                        brand='ASDA',
                        name=station_data.get('name', ''),
                        postcode=station_data.get('postcode', ''),
                        address=station_data.get('address', ''),
                        prices=station_data.get('prices', {})
                    )
                    stations.append(station)
                except (KeyError, TypeError) as e:
                    print(f"Error parsing ASDA station: {e}")
                    continue
        return stations

class SainsburysAPI(FuelPriceAPI):
    """Sainsbury's fuel price API implementation"""
    
    def __init__(self):
        super().__init__("Sainsbury's", "https://api.sainsburys.co.uk/v1/exports/latest/fuel_prices_data.json")
    
    def parse_stations(self, data: Dict) -> List[FuelStation]:
        stations = []
        if 'stations' in data:
            for station_data in data['stations']:
                try:
                    station = FuelStation(
                        site_id=str(station_data.get('site_id', '')),
                        brand='Sainsburys',
                        name=station_data.get('name', ''),
                        postcode=station_data.get('postcode', ''),
                        address=station_data.get('address', ''),
                        prices=station_data.get('prices', {})
                    )
                    stations.append(station)
                except (KeyError, TypeError) as e:
                    print(f"Error parsing Sainsburys station: {e}")
                    continue
        return stations

class TescoAPI(FuelPriceAPI):
    """Tesco fuel price API implementation"""
    
    def __init__(self):
        super().__init__("Tesco", "https://www.tesco.com/fuel_prices/fuel_prices_data.json")
    
    def parse_stations(self, data: Dict) -> List[FuelStation]:
        stations = []
        if 'stations' in data:
            for station_data in data['stations']:
                try:
                    station = FuelStation(
                        site_id=str(station_data.get('site_id', '')),
                        brand='Tesco',
                        name=station_data.get('name', ''),
                        postcode=station_data.get('postcode', ''),
                        address=station_data.get('address', ''),
                        prices=station_data.get('prices', {})
                    )
                    stations.append(station)
                except (KeyError, TypeError) as e:
                    print(f"Error parsing Tesco station: {e}")
                    continue
        return stations

class PostcodeUtils:
    """Utilities for working with UK postcodes"""
    
    @staticmethod
    def normalize_postcode(postcode: str) -> str:
        """Normalize postcode format"""
        return postcode.upper().replace(' ', '')
    
    @staticmethod
    def parse_postcode(postcode: str) -> PostcodeInfo:
        """Parse a UK postcode into components"""
        normalized = PostcodeUtils.normalize_postcode(postcode)
        
        # Extract outcode (first part before the number)
        outcode_match = re.match(r'^([A-Z]{1,2}[0-9]{1,2}[A-Z]?)', normalized)
        outcode = outcode_match.group(1) if outcode_match else ''
        
        # Extract area (first 1-2 letters)
        area_match = re.match(r'^([A-Z]{1,2})', normalized)
        area = area_match.group(1) if area_match else ''
        
        return PostcodeInfo(
            full_postcode=normalized,
            outcode=outcode,
            area=area
        )

class FuelPriceAnalyzer:
    """Main analyzer class that coordinates fuel price fetching and analysis"""
    
    def __init__(self):
        self.apis = [
            AsdaAPI(),
            SainsburysAPI(),
            TescoAPI()
        ]
        self.stations_cache = {}
    
    def fetch_all_stations(self, use_cache: bool = True) -> Dict[str, List[FuelStation]]:
        """Fetch stations from all APIs"""
        if use_cache and self.stations_cache:
            return self.stations_cache
        
        all_stations = {}
        for api in self.apis:
            data = api.fetch_data()
            if data:
                stations = api.parse_stations(data)
                all_stations[api.name] = stations
                print(f"✓ {api.name}: {len(stations)} stations loaded")
            else:
                all_stations[api.name] = []
                print(f"✗ {api.name}: Failed to load stations")
        
        self.stations_cache = all_stations
        return all_stations
    
    def find_stations_by_postcode(self, target_postcode: str) -> Dict[str, FuelStation]:
        """Find the best station for each brand near the target postcode"""
        postcode_info = PostcodeUtils.parse_postcode(target_postcode)
        all_stations = self.fetch_all_stations()
        
        best_stations = {}
        
        for brand, stations in all_stations.items():
            selected_station = None
            
            # First try exact postcode match
            for station in stations:
                station_pc = PostcodeUtils.normalize_postcode(station.postcode)
                if station_pc == postcode_info.full_postcode:
                    selected_station = station
                    break
            
            # Then try outcode match
            if not selected_station and postcode_info.outcode:
                for station in stations:
                    station_pc = PostcodeUtils.normalize_postcode(station.postcode)
                    if station_pc.startswith(postcode_info.outcode):
                        selected_station = station
                        break
            
            # Finally try area match
            if not selected_station and postcode_info.area:
                for station in stations:
                    station_pc = PostcodeUtils.normalize_postcode(station.postcode)
                    if station_pc.startswith(postcode_info.area):
                        selected_station = station
                        break
            
            if selected_station:
                best_stations[brand] = selected_station
        
        return best_stations
    
    def get_diesel_prices_summary(self, target_postcode: str) -> Dict[str, Dict]:
        """Get a summary of diesel prices for the target postcode"""
        stations = self.find_stations_by_postcode(target_postcode)
        summary = {}
        
        for brand, station in stations.items():
            diesel_price = station.get_diesel_price()
            summary[brand] = {
                'station_id': station.site_id,
                'station_name': station.name,
                'postcode': station.postcode,
                'diesel_price_per_litre': diesel_price,
                'diesel_price_per_kwh': diesel_price / 10 if diesel_price else None,  # ~10 kWh per litre
                'available_fuels': list(station.prices.keys()),
                'all_prices': station.prices
            }
        
        return summary
    
    def compare_all_prices(self, target_postcode: str) -> None:
        """Print a comparison of all fuel prices"""
        summary = self.get_diesel_prices_summary(target_postcode)
        
        print(f"\n🔍 Fuel Price Analysis for {target_postcode}")
        print("=" * 60)
        
        diesel_prices = []
        for brand, data in summary.items():
            diesel_price = data['diesel_price_per_litre']
            price_kwh = data['diesel_price_per_kwh']
            
            if diesel_price:
                diesel_prices.append((brand, diesel_price))
                print(f"\n{brand}:")
                print(f"  Station: {data['station_name']}")
                print(f"  Postcode: {data['postcode']}")
                print(f"  Diesel: £{diesel_price:.3f}/L (£{price_kwh:.4f}/kWh)")
                print(f"  Available fuels: {', '.join(data['available_fuels'])}")
            else:
                print(f"\n{brand}:")
                print(f"  ❌ No diesel price available")
        
        if diesel_prices:
            # Find cheapest
            cheapest = min(diesel_prices, key=lambda x: x[1])
            most_expensive = max(diesel_prices, key=lambda x: x[1])
            
            print(f"\n💰 Price Comparison:")
            print(f"  Cheapest: {cheapest[0]} at £{cheapest[1]:.3f}/L")
            print(f"  Most expensive: {most_expensive[0]} at £{most_expensive[1]:.3f}/L")
            
            if len(diesel_prices) > 1:
                savings = most_expensive[1] - cheapest[1]
                print(f"  Potential saving: £{savings:.3f}/L")

def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze fuel prices near a postcode")
    parser.add_argument("postcode", help="UK postcode to search near")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--brand", help="Filter to specific brand (ASDA, Sainsburys, Tesco)")
    
    args = parser.parse_args()
    
    analyzer = FuelPriceAnalyzer()
    
    if args.json:
        summary = analyzer.get_diesel_prices_summary(args.postcode)
        if args.brand:
            summary = {k: v for k, v in summary.items() if k.upper() == args.brand.upper()}
        print(json.dumps(summary, indent=2))
    else:
        analyzer.compare_all_prices(args.postcode)

if __name__ == "__main__":
    main()