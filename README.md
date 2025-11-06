# PyEphEmber Home Assistant Integration

This repository contains the production-ready EPH Controls integration for Home Assistant.

## Production Files

### Core Integration
- `eph_helper.py` - Production EPH Controls helper script for Home Assistant integration
- `final_corrected_config.yaml` - Main Home Assistant configuration with EPH sensors and climate control

### Home Assistant Packages
- `corrected_heating_analytics_package.yaml` - Heating cycle tracking and efficiency analytics
- `corrected_luften_eph.yaml` - Lüften (ventilation) integration with EPH heating data

### Automations & UI
- `corrected_eph_automations.yaml` - EPH temperature synchronization automations
- `corrected_heating_dashboard.yaml` - Heating analytics dashboard
- `improved_quick_actions.yaml` - Quick action cards for heating control

## Installation

1. Copy `eph_helper.py` to `/root/config/scripts/` on your Home Assistant host
2. Create `/root/config/scripts/.env` with your EPH credentials:
   ```
   EPH_USERNAME=your_email@example.com
   EPH_PASSWORD=your_password
   ```
3. Copy package files to `/root/config/packages/`
4. Add configuration from `final_corrected_config.yaml` to your main configuration
5. Add automations from `corrected_eph_automations.yaml` to your automations.yaml
6. Restart Home Assistant

## Features

- Real-time EPH zone temperature monitoring
- Target temperature control via Home Assistant
- Heating cycle analytics and efficiency tracking
- Integration with InfluxDB for long-term data storage
- Mobile-friendly heating dashboard
- Automated temperature synchronization

## Requirements

- Home Assistant with packages support enabled
- pyephember2 installed in Home Assistant Python environment
- EPH Controls account and zone access