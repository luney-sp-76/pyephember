# Fuel Price APIs for Cost Analysis

This document lists the available fuel price APIs that can be used to calculate heating oil cost per kWh.

## Available APIs

### Working APIs (JSON format)
- **Ascona Group**: https://fuelprices.asconagroup.co.uk/newfuel.json
- **Asda**: https://storelocator.asda.com/fuel_prices_data.json
- **bp**: https://www.bp.com/en_gb/united-kingdom/home/fuelprices/fuel_prices_data.json
- **Esso Tesco Alliance**: https://fuelprices.esso.co.uk/latestdata.json
- **JET Retail UK**: https://jetlocal.co.uk/fuel_prices_data.json
- **Karan Retail Ltd**: https://api.krl.live/integration/live_price/krl
- **Morrisons**: https://www.morrisons.com/fuel-prices/fuel.json
- **Moto**: https://moto-way.com/fuel-price/fuel_prices.json
- **Motor Fuel Group**: https://fuel.motorfuelgroup.com/fuel_prices_data.json
- **Rontec**: https://www.rontec-servicestations.co.uk/fuel-prices/data/fuel_prices_data.json
- **Sainsbury's**: https://api.sainsburys.co.uk/v1/exports/latest/fuel_prices_data.json
- **SGN**: https://www.sgnretail.uk/files/data/SGN_daily_fuel_prices.json
- **Tesco**: https://www.tesco.com/fuel_prices/fuel_prices_data.json

### Special Format
- **Shell**: https://www.shell.co.uk/fuel-prices-data.html (HTML page, requires parsing)

## Fuel Types for Heating Cost Analysis

For heating oil cost calculation, we need:
- **Heating Oil** (red diesel/kerosene)
- **Diesel** (as proxy for heating oil prices)
- **Gas Oil** (if available)

## Energy Content Reference

- **Heating Oil**: ~10 kWh per litre
- **Diesel**: ~10 kWh per litre
- **Kerosene**: ~9.8 kWh per litre