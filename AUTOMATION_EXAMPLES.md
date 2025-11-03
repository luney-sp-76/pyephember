# 🤖 EPH Ember Automation Examples

Once your EPH Ember integration is configured, here are some useful automations to get you started.

## 🌅 Morning Heating Boost

Heat up the house before you wake up on weekdays:

```yaml
# automations.yaml
- alias: "Morning Heating Boost"
  description: "Boost heating in living areas before wake up time"
  trigger:
    - platform: time
      at: "06:30:00"  # 30 minutes before wake up
  condition:
    - condition: time
      weekday:
        - mon
        - tue  
        - wed
        - thu
        - fri
    - condition: numeric_state
      entity_id: sensor.outdoor_temperature  # If you have outdoor sensor
      below: 10  # Only when it's cold outside
  action:
    - service: climate.set_temperature
      target:
        entity_id: climate.living_room
      data:
        temperature: 22
    - service: climate.set_temperature
      target:
        entity_id: climate.kitchen
      data:
        temperature: 20
```

## 🌙 Evening Setback

Reduce heating when going to bed:

```yaml
- alias: "Evening Heating Setback"
  description: "Lower temperature at bedtime"
  trigger:
    - platform: time
      at: "22:00:00"
  action:
    - service: climate.set_temperature
      target:
        entity_id: 
          - climate.living_room
          - climate.kitchen
      data:
        temperature: 16
    - service: climate.set_temperature
      target:
        entity_id: climate.bedroom
      data:
        temperature: 18
```

## 🚶 Presence-Based Heating

Only heat when someone is home:

```yaml
- alias: "Away Mode Heating"
  description: "Lower heating when nobody is home"
  trigger:
    - platform: state
      entity_id: group.family  # Your person group
      to: 'not_home'
      for: "00:30:00"  # After 30 minutes away
  action:
    - service: climate.set_temperature
      target:
        entity_id: 
          - climate.living_room
          - climate.bedroom
          - climate.kitchen
      data:
        temperature: 15  # Frost protection

- alias: "Home Mode Heating" 
  description: "Resume normal heating when someone comes home"
  trigger:
    - platform: state
      entity_id: group.family
      to: 'home'
  action:
    - service: climate.set_temperature
      target:
        entity_id: climate.living_room
      data:
        temperature: 20
```

## 🌡️ Smart Temperature Control

Adjust heating based on outside temperature:

```yaml
- alias: "Smart Heating Adjustment"
  description: "Adjust indoor temperature based on outdoor conditions"
  trigger:
    - platform: time_pattern
      hours: "/2"  # Every 2 hours
  condition:
    - condition: state
      entity_id: group.family
      state: 'home'
  action:
    - choose:
        - conditions:
            - condition: numeric_state
              entity_id: sensor.outdoor_temperature
              below: 0  # Very cold
          sequence:
            - service: climate.set_temperature
              target:
                entity_id: climate.living_room
              data:
                temperature: 22
        - conditions:
            - condition: numeric_state
              entity_id: sensor.outdoor_temperature
              above: 15  # Mild weather
          sequence:
            - service: climate.set_temperature
              target:
                entity_id: climate.living_room
              data:
                temperature: 18
      default:
        - service: climate.set_temperature
          target:
            entity_id: climate.living_room
          data:
            temperature: 20
```

## 💰 Energy Saving Mode

Activate energy saving during peak hours:

```yaml
- alias: "Energy Peak Hours Setback"
  description: "Reduce heating during expensive electricity hours"
  trigger:
    - platform: time
      at: "16:00:00"  # Peak hours start
  condition:
    - condition: time
      weekday:
        - mon
        - tue
        - wed
        - thu
        - fri
  action:
    - service: climate.set_temperature
      target:
        entity_id:
          - climate.living_room
          - climate.bedroom
      data:
        temperature: "{{ state_attr(trigger.entity_id, 'temperature') | float - 2 }}"
    - service: notify.mobile_app_your_phone
      data:
        message: "🔋 Energy saving mode activated - heating reduced by 2°C"

- alias: "Energy Peak Hours End"
  trigger:
    - platform: time
      at: "20:00:00"  # Peak hours end
  action:
    - service: climate.set_temperature
      target:
        entity_id:
          - climate.living_room  
          - climate.bedroom
      data:
        temperature: "{{ state_attr(trigger.entity_id, 'temperature') | float + 2 }}"
```

## 🔔 Heating Notifications

Get notified about heating events:

```yaml
- alias: "Heating Zone Offline Alert"
  description: "Alert when a heating zone goes offline"
  trigger:
    - platform: state
      entity_id:
        - climate.living_room
        - climate.bedroom
        - climate.kitchen
      to: 'unavailable'
      for: "00:05:00"
  action:
    - service: notify.mobile_app_your_phone
      data:
        title: "⚠️ Heating Alert"
        message: "Zone {{ trigger.to_state.attributes.friendly_name }} is offline"
        data:
          priority: high

- alias: "Temperature Target Reached"
  description: "Notify when target temperature is reached"
  trigger:
    - platform: template
      value_template: >
        {{ 
          (states('sensor.living_room_temperature') | float) >= 
          (state_attr('climate.living_room', 'temperature') | float)
        }}
  action:
    - service: notify.mobile_app_your_phone
      data:
        message: "🌡️ Living room has reached {{ state_attr('climate.living_room', 'temperature') }}°C"
```

## 🏠 Scene-Based Heating

Create heating scenes for different scenarios:

```yaml
# scripts.yaml
comfort_mode:
  alias: "Comfort Heating Mode"
  sequence:
    - service: climate.set_temperature
      target:
        entity_id: climate.living_room
      data:
        temperature: 22
    - service: climate.set_temperature
      target:
        entity_id: climate.bedroom
      data:
        temperature: 19
    - service: climate.set_temperature
      target:
        entity_id: climate.kitchen
      data:
        temperature: 20

eco_mode:
  alias: "Eco Heating Mode"
  sequence:
    - service: climate.set_temperature
      target:
        entity_id:
          - climate.living_room
          - climate.bedroom
          - climate.kitchen
      data:
        temperature: 16

guest_mode:
  alias: "Guest Mode Heating"
  sequence:
    - service: climate.set_temperature
      target:
        entity_id: climate.guest_room
      data:
        temperature: 20
    - service: climate.set_temperature
      target:
        entity_id: climate.living_room
      data:
        temperature: 21
```

## 📱 Quick Dashboard Buttons

Add these to your dashboard for manual control:

```yaml
# Dashboard card
type: horizontal-stack
cards:
  - type: button
    tap_action:
      action: call-service
      service: script.comfort_mode
    name: "Comfort"
    icon: mdi:sofa
    
  - type: button
    tap_action:
      action: call-service
      service: script.eco_mode
    name: "Eco"
    icon: mdi:leaf
    
  - type: button
    tap_action:
      action: call-service
      service: climate.set_temperature
      service_data:
        entity_id: climate.living_room
        temperature: 24
    name: "Boost"
    icon: mdi:fire
    hold_action:
      action: more-info
```

## ⚙️ Advanced: Template Climate Control

Create a template that automatically adjusts based on multiple factors:

```yaml
# configuration.yaml
template:
  - sensor:
      - name: "Smart Target Temperature"
        state: >
          {% set outdoor_temp = states('sensor.outdoor_temperature') | float %}
          {% set time_of_day = now().hour %}
          {% set is_home = is_state('group.family', 'home') %}
          {% set is_weekend = now().weekday() in [5, 6] %}
          
          {% if not is_home %}
            15
          {% elif time_of_day >= 23 or time_of_day < 6 %}
            {% if is_weekend %}19{% else %}17{% endif %}
          {% elif outdoor_temp < 0 %}
            22
          {% elif outdoor_temp < 10 %}
            20
          {% else %}
            18
          {% endif %}

# Use in automation
- alias: "Apply Smart Temperature"
  trigger:
    - platform: state
      entity_id: sensor.smart_target_temperature
    - platform: time_pattern
      minutes: "/30"
  action:
    - service: climate.set_temperature
      target:
        entity_id: climate.living_room
      data:
        temperature: "{{ states('sensor.smart_target_temperature') | float }}"
```

## 🔧 Troubleshooting Automations

### Test Your Automations:
```yaml
# Add a test automation
- alias: "EPH Test Automation"
  trigger:
    - platform: state
      entity_id: input_boolean.test_heating  # Create this helper first
      to: 'on'
  action:
    - service: climate.set_temperature
      target:
        entity_id: climate.living_room
      data:
        temperature: 21
    - service: notify.persistent_notification.create
      data:
        message: "✅ EPH Ember automation test successful!"
    - service: input_boolean.turn_off
      target:
        entity_id: input_boolean.test_heating
```

### Debug Climate Entities:
Go to **Developer Tools** → **Services** and test:
- Service: `climate.set_temperature`
- Entity: `climate.living_room`
- Temperature: `20`

---

**💡 Pro Tips:**
1. Start with simple time-based automations
2. Test each automation individually
3. Use the trace feature to debug automation issues
4. Consider outdoor temperature sensors for smarter control
5. Set up notifications for important heating events

**🚀 Ready to automate your heating!** Copy and paste these examples, adjusting entity names to match your zones.