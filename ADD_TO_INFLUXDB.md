# Add Heating Entities to Existing InfluxDB Configuration

Since you already have InfluxDB configured, you just need to add the heating entities to your existing configuration.

## **Step 1: Update Your Existing InfluxDB Configuration**

Find your InfluxDB configuration in `configuration.yaml` and add the heating entities to the `include: entities:` section:

```yaml
# Your existing InfluxDB configuration in configuration.yaml
influxdb:
  # Your existing settings (host, port, database, etc.)
  host: your_host
  port: 8086
  database: your_database
  # ... other existing settings ...
  
  include:
    entities:
      # Your existing entities...
      
      # ADD THESE HEATING ENTITIES:
      - binary_sensor.zone_one_heating_active
      - counter.zone_one_heating_cycles_today
      - sensor.zone_one_average_heating_duration
      - input_number.zone_one_total_heating_time_today
      - sensor.daily_heating_efficiency_zone_one
      - climate.one
      - sensor.zone_one_heating_time_today
      - sensor.zone_one_heating_cycles_count_today
      - input_datetime.zone_one_heating_start
      
      # ADD THESE NEW COST SENSORS (from the package):
      - sensor.daily_heating_cost
      - sensor.monthly_heating_cost_projection
      - sensor.heating_efficiency_trend
      
      # ADD STATISTICS SENSORS:
      - sensor.monthly_heating_cycles_average
      - sensor.monthly_average_heating_duration
      - sensor.weekly_heating_efficiency
      - sensor.monthly_total_heating_time
```

## **Step 2: Use the Package for Analytics**

The package file `influxdb_heating_config.yaml` contains:
- ✅ **Statistics sensors** for long-term trending
- ✅ **Utility meters** for cost tracking
- ✅ **Template sensors** for cost calculations
- ✅ **All non-InfluxDB configurations**

This way you get all the analytics without conflicting with your existing InfluxDB setup!

## **Step 3: Restart Home Assistant**

After adding the heating entities to your InfluxDB configuration:
1. **Save configuration.yaml**
2. **Restart Home Assistant**
3. **Verify entities appear in InfluxDB**

## **Step 4: Check InfluxDB Data**

You can verify the data is being stored:

```sql
-- Connect to your InfluxDB
influx -database your_database_name

-- Check for heating data
SHOW MEASUREMENTS

-- Query recent heating activity
SELECT * FROM state WHERE entity_id = 'binary_sensor.zone_one_heating_active' AND time > now() - 1h
```

This approach lets you keep your existing InfluxDB configuration while adding comprehensive heating analytics! 🔥📊