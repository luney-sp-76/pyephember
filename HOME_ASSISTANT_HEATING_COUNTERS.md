# Home Assistant Configuration for Heating Transition Counting

## 📊 Track Heating Cycles with Sensors

Add this to your `configuration.yaml` to track heating transitions:

```yaml
# Configuration.yaml
template:
  - binary_sensor:
      # Track when each zone is actively heating
      - name: "Living Room Heating Active"
        state: "{{ is_state('climate.living_room', 'heat') and state_attr('climate.living_room', 'hvac_action') == 'heating' }}"
        device_class: heat
        
      - name: "Bedroom Heating Active"  
        state: "{{ is_state('climate.bedroom', 'heat') and state_attr('climate.bedroom', 'hvac_action') == 'heating' }}"
        device_class: heat
        
      - name: "Kitchen Heating Active"
        state: "{{ is_state('climate.kitchen', 'heat') and state_attr('climate.kitchen', 'hvac_action') == 'heating' }}"
        device_class: heat

  - sensor:
      # Count heating cycles (transitions from off to on)
      - name: "Living Room Heating Cycles Today"
        state: >
          {{ states('counter.living_room_heating_cycles') | int }}
        unit_of_measurement: "cycles"
        icon: mdi:counter
        
      - name: "Bedroom Heating Cycles Today"
        state: >
          {{ states('counter.bedroom_heating_cycles') | int }}
        unit_of_measurement: "cycles"
        icon: mdi:counter
        
      - name: "Kitchen Heating Cycles Today"
        state: >
          {{ states('counter.kitchen_heating_cycles') | int }}
        unit_of_measurement: "cycles"
        icon: mdi:counter
        
      # Total heating time today
      - name: "Living Room Heating Time Today"
        state: >
          {{ states('sensor.living_room_heating_time_today') | float }}
        unit_of_measurement: "h"
        icon: mdi:clock-outline
        
      # Efficiency metric: average cycle length
      - name: "Living Room Average Cycle Length"
        state: >
          {% set cycles = states('counter.living_room_heating_cycles') | int %}
          {% set time = states('sensor.living_room_heating_time_today') | float %}
          {% if cycles > 0 %}
            {{ (time / cycles) | round(1) }}
          {% else %}
            0
          {% endif %}
        unit_of_measurement: "h"
        icon: mdi:chart-line

# Create counters for each zone
counter:
  living_room_heating_cycles:
    name: Living Room Heating Cycles
    icon: mdi:fire
    
  bedroom_heating_cycles:
    name: Bedroom Heating Cycles  
    icon: mdi:fire
    
  kitchen_heating_cycles:
    name: Kitchen Heating Cycles
    icon: mdi:fire

# Track heating time with history_stats
sensor:
  - platform: history_stats
    name: Living Room Heating Time Today
    entity_id: binary_sensor.living_room_heating_active
    state: 'on'
    type: time
    start: '{{ now().replace(hour=0, minute=0, second=0) }}'
    end: '{{ now() }}'
    
  - platform: history_stats
    name: Bedroom Heating Time Today
    entity_id: binary_sensor.bedroom_heating_active
    state: 'on'
    type: time
    start: '{{ now().replace(hour=0, minute=0, second=0) }}'
    end: '{{ now() }}'
    
  - platform: history_stats
    name: Kitchen Heating Time Today
    entity_id: binary_sensor.kitchen_heating_active
    state: 'on'
    type: time
    start: '{{ now().replace(hour=0, minute=0, second=0) }}'
    end: '{{ now() }}'
```

## 🤖 Automations to Count Transitions

```yaml
# automations.yaml

# Count heating cycles (off -> on transitions)
- alias: "Count Living Room Heating Cycles"
  description: "Increment counter when living room heating turns on"
  trigger:
    - platform: state
      entity_id: binary_sensor.living_room_heating_active
      from: 'off'
      to: 'on'
  action:
    - service: counter.increment
      target:
        entity_id: counter.living_room_heating_cycles
    - service: logbook.log
      data:
        name: "Heating Tracker"
        message: "Living room heating cycle started ({{ states('counter.living_room_heating_cycles') }})"

- alias: "Count Bedroom Heating Cycles"
  description: "Increment counter when bedroom heating turns on"
  trigger:
    - platform: state
      entity_id: binary_sensor.bedroom_heating_active
      from: 'off'
      to: 'on'
  action:
    - service: counter.increment
      target:
        entity_id: counter.bedroom_heating_cycles

- alias: "Count Kitchen Heating Cycles"  
  description: "Increment counter when kitchen heating turns on"
  trigger:
    - platform: state
      entity_id: binary_sensor.kitchen_heating_active
      from: 'off'
      to: 'on'
  action:
    - service: counter.increment
      target:
        entity_id: counter.kitchen_heating_cycles

# Reset counters daily at midnight
- alias: "Reset Daily Heating Counters"
  description: "Reset heating cycle counters at midnight"
  trigger:
    - platform: time
      at: "00:00:00"
  action:
    - service: counter.reset
      target:
        entity_id:
          - counter.living_room_heating_cycles
          - counter.bedroom_heating_cycles  
          - counter.kitchen_heating_cycles

# Weekly heating efficiency report
- alias: "Weekly Heating Report"
  description: "Send weekly heating efficiency summary"
  trigger:
    - platform: time
      at: "09:00:00"
    - platform: time
      weekday: 
        - sun
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "📊 Weekly Heating Report"
        message: >
          Living Room: {{ states('sensor.living_room_heating_cycles_weekly') }} cycles, 
          {{ states('sensor.living_room_heating_time_weekly') }}h total.
          Average cycle: {{ states('sensor.living_room_average_cycle_length') }}h
```

## 📱 Dashboard Cards

Add these cards to track heating cycles:

```yaml
# Heating Efficiency Dashboard
type: vertical-stack
cards:
  # Cycle counters
  - type: horizontal-stack
    cards:
      - type: statistic
        entity: sensor.living_room_heating_cycles_today
        name: "Living Room Cycles"
        
      - type: statistic
        entity: sensor.bedroom_heating_cycles_today
        name: "Bedroom Cycles"
        
      - type: statistic
        entity: sensor.kitchen_heating_cycles_today
        name: "Kitchen Cycles"
  
  # Heating time today
  - type: horizontal-stack
    cards:
      - type: statistic
        entity: sensor.living_room_heating_time_today
        name: "Living Room Time"
        
      - type: statistic
        entity: sensor.living_room_average_cycle_length
        name: "Avg Cycle Length"
  
  # Historical chart
  - type: history-graph
    entities:
      - counter.living_room_heating_cycles
      - counter.bedroom_heating_cycles
      - counter.kitchen_heating_cycles
    hours_to_show: 24
    refresh_interval: 300

  # Real-time heating status
  - type: entities
    entities:
      - binary_sensor.living_room_heating_active
      - binary_sensor.bedroom_heating_active
      - binary_sensor.kitchen_heating_active
    title: "Current Heating Status"
    state_color: true
```

## 🔧 Advanced: Weekly/Monthly Tracking

```yaml
# Add to configuration.yaml for longer-term tracking
sensor:
  # Weekly statistics  
  - platform: history_stats
    name: Living Room Heating Cycles Weekly
    entity_id: binary_sensor.living_room_heating_active
    state: 'on'
    type: count
    start: '{{ as_timestamp(now().replace(hour=0, minute=0, second=0)) - (now().weekday() * 86400) }}'
    end: '{{ now() }}'
    
  - platform: history_stats
    name: Living Room Heating Time Weekly
    entity_id: binary_sensor.living_room_heating_active
    state: 'on'
    type: time
    start: '{{ as_timestamp(now().replace(hour=0, minute=0, second=0)) - (now().weekday() * 86400) }}'
    end: '{{ now() }}'

# Monthly heating cost estimation
template:
  - sensor:
      - name: "Estimated Monthly Heating Cost"
        state: >
          {% set hours = states('sensor.living_room_heating_time_monthly') | float %}
          {% set kwh_per_hour = 3 %}  # Adjust based on your boiler
          {% set cost_per_kwh = 0.28 %}  # Adjust based on your electricity rate
          {{ (hours * kwh_per_hour * cost_per_kwh) | round(2) }}
        unit_of_measurement: "£"
        icon: mdi:currency-gbp
```

## 💡 **What This Gives You:**

1. **Daily heating cycle counts** for each zone
2. **Total heating time** per zone per day
3. **Average cycle length** (efficiency metric)
4. **Weekly/monthly summaries**
5. **Real-time heating status**
6. **Cost estimation** based on usage
7. **Historical graphs** and trends

## 🎯 **Usage:**

1. **Monitor efficiency**: Short, frequent cycles might indicate poor insulation
2. **Compare zones**: See which rooms need heating most
3. **Track improvements**: Monitor changes after insulation upgrades
4. **Cost tracking**: Estimate heating costs based on actual usage
5. **Maintenance alerts**: Unusual cycle patterns might indicate issues

The key insight is that **the PyEphEmber library doesn't have built-in transition counting**, but Home Assistant can track state changes and count them automatically! 📊