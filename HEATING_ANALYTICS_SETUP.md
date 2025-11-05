# 🔥 Daily Heating Cycle Counter & Duration Tracker Setup Guide

This comprehensive system tracks:
- ✅ **Daily count** of heating on/off cycles per zone
- ✅ **Average duration** from heat on to heat off
- ✅ **Total heating time** per zone per day
- ✅ **Efficiency metrics** and insights
- ✅ **Cost estimates** based on usage
- ✅ **Alerts** for unusual patterns

## 📁 File Structure

```
/config/
├── configuration.yaml          # Add heating_cycle_tracker.yaml content
├── automations.yaml           # Add heating_tracker_automations.yaml content
└── ui-lovelace.yaml           # Add heating_dashboard.yaml content
```

## 🚀 Installation Steps

### Step 1: Add Configuration
Copy the content from `heating_cycle_tracker.yaml` and add it to your `configuration.yaml`:

```yaml
# Add this to configuration.yaml
# ... (paste the counter, input_datetime, input_number, and template sections)
```

### Step 2: Add Automations
Copy the content from `heating_tracker_automations.yaml` and add it to your `automations.yaml`:

```yaml
# Add this to automations.yaml  
# ... (paste all the automation rules)
```

### Step 3: Create Dashboard
Create a new dashboard or add the cards from `heating_dashboard.yaml` to your existing dashboard.

### Step 4: Customize Entity Names
**IMPORTANT:** Update these entity names to match your actual EPH Ember climate entities:

```yaml
# Replace these in ALL files:
climate.living_room    → climate.your_actual_living_room_entity
climate.bedroom        → climate.your_actual_bedroom_entity
climate.kitchen        → climate.your_actual_kitchen_entity
```

## 🔧 Finding Your Entity Names

In Home Assistant:
1. Go to **Settings** → **Devices & Services**
2. Find your **EPH Ember** integration
3. Click on it to see all entities
4. Note the exact `entity_id` names (e.g., `climate.zone_1_living_room`)

## 📊 What You'll Get

### Daily Metrics:
- **Cycle Count**: Number of times heating switched on today
- **Average Duration**: Average time from on→off per cycle
- **Total Time**: Total heating time for the day
- **Efficiency Rating**: Poor/Good/Excellent based on cycle patterns

### Dashboard Features:
- 🔴/🟢 **Real-time status** indicators for each zone
- 📈 **Historical graphs** showing heating patterns
- 💰 **Cost estimates** based on your electricity rates
- 🎯 **Efficiency insights** and recommendations
- ⚠️ **Alerts** for unusual heating patterns

### Automatic Features:
- **Daily reset** at midnight
- **Daily summary** notifications at 11 PM
- **Weekly reports** on Sundays
- **Unusual pattern alerts** (too many/few cycles)

## 🎯 Usage Examples

### View Today's Stats:
```
Living Room: 8 cycles, 15.3 min average, 122 min total
Bedroom: 5 cycles, 12.1 min average, 61 min total  
Kitchen: 3 cycles, 18.7 min average, 56 min total
```

### Efficiency Insights:
- **Short cycles** (< 10 min): Check insulation, system may be oversized
- **Long cycles** (> 30 min): Excellent efficiency, good insulation
- **Many cycles** (> 20/day): Temperature settings may be too aggressive

### Cost Tracking:
- **Daily cost**: £3.50 (based on 2.1 hours total heating)
- **Projected monthly**: £105 (based on current usage pattern)

## 🔧 Customization Options

### Adjust Cost Calculation:
In the dashboard template, modify these values:
```yaml
{% set kwh_per_hour = 3 %}      # Your boiler's kW rating
{% set cost_per_kwh = 0.28 %}   # Your electricity rate (£ per kWh)
```

### Change Alert Thresholds:
In the automations, adjust:
```yaml
above: 50    # Alert when more than 50 cycles per day
below: 3     # Alert when average cycle < 3 minutes
```

### Add More Zones:
Copy and modify the patterns for additional zones:
1. Add counter for new zone
2. Add binary_sensor for heating detection
3. Add automations for counting/duration
4. Add dashboard cards

## 🧪 Testing the Setup

### Test Heating Detection:
1. Manually change temperature on a zone
2. Check that `binary_sensor.xxx_heating_active` shows "on"
3. Verify counter increments when heating starts

### Test Duration Calculation:
1. Let heating run for a few minutes
2. Turn off heating or lower temperature
3. Check that total time increases appropriately

### Verify Daily Reset:
Wait until midnight or manually trigger:
```yaml
service: automation.trigger
target:
  entity_id: automation.reset_daily_heating_counters
```

## 📱 Mobile Notifications

To receive notifications, update this entity in automations:
```yaml
service: notify.mobile_app_your_phone  # Replace with your device
```

Find your notification service in **Settings** → **Devices & Services** → **Mobile App**.

## 🔍 Troubleshooting

### Counters Not Incrementing:
- Check that climate entities are correct
- Verify binary sensors show "on" when heating is active
- Look at automation traces in **Settings** → **Automations**

### Duration Calculation Wrong:
- Check that `input_datetime` entities are being set
- Verify timezone settings in Home Assistant
- Test automation triggers manually

### Dashboard Not Showing Data:
- Restart Home Assistant after adding configuration
- Check for YAML syntax errors in **Settings** → **System** → **Logs**
- Verify entity names match exactly

## 🎉 Ready to Track Your Heating!

Once installed, you'll have comprehensive heating analytics that help you:
- **Optimize efficiency** by understanding heating patterns
- **Reduce costs** by identifying wasteful heating cycles
- **Monitor system health** through cycle duration analysis
- **Track improvements** after insulation or system changes

**Your heating system will never be a mystery again!** 🔥📊