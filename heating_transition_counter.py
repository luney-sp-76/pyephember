#!/usr/bin/env python3
"""
Heating State Transition Counter for EPH Ember

This script monitors heating zones and counts transitions from OFF to ON.
Useful for tracking heating cycles and system efficiency.
"""

import time
import datetime
import json
import os
from pyephember.pyephember import EphEmber

class HeatingTransitionCounter:
    """
    Tracks heating state transitions and counts on/off cycles
    """
    
    def __init__(self, email, password, state_file='heating_state.json'):
        self.ember = EphEmber(email, password)
        self.state_file = state_file
        self.previous_states = {}
        self.transition_counts = {}
        self.load_state()
    
    def load_state(self):
        """Load previous states and counts from file"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)
                    self.previous_states = data.get('previous_states', {})
                    self.transition_counts = data.get('transition_counts', {})
            except Exception as e:
                print(f"Error loading state: {e}")
    
    def save_state(self):
        """Save current states and counts to file"""
        data = {
            'previous_states': self.previous_states,
            'transition_counts': self.transition_counts,
            'last_updated': datetime.datetime.now().isoformat()
        }
        try:
            with open(self.state_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")
    
    def check_zone_transition(self, zone_name):
        """
        Check if a zone has transitioned from OFF to ON
        Returns True if transition occurred
        """
        try:
            # Get current states
            is_active = self.ember.is_zone_active(zone_name)
            boiler_on = self.ember.is_zone_boiler_on(zone_name)
            
            # Initialize if first time checking this zone
            if zone_name not in self.previous_states:
                self.previous_states[zone_name] = {
                    'active': is_active,
                    'boiler': boiler_on
                }
                self.transition_counts[zone_name] = {
                    'active_transitions': 0,
                    'boiler_transitions': 0,
                    'last_active_transition': None,
                    'last_boiler_transition': None
                }
                return False
            
            prev_active = self.previous_states[zone_name]['active']
            prev_boiler = self.previous_states[zone_name]['boiler']
            
            transition_occurred = False
            
            # Check for active state transition (OFF -> ON)
            if not prev_active and is_active:
                self.transition_counts[zone_name]['active_transitions'] += 1
                self.transition_counts[zone_name]['last_active_transition'] = datetime.datetime.now().isoformat()
                print(f"🔥 Zone '{zone_name}' heating activated! (Count: {self.transition_counts[zone_name]['active_transitions']})")
                transition_occurred = True
            
            # Check for boiler transition (OFF -> ON) - actual fuel burning
            if not prev_boiler and boiler_on:
                self.transition_counts[zone_name]['boiler_transitions'] += 1
                self.transition_counts[zone_name]['last_boiler_transition'] = datetime.datetime.now().isoformat()
                print(f"🔥 Zone '{zone_name}' boiler ignited! (Count: {self.transition_counts[zone_name]['boiler_transitions']})")
                transition_occurred = True
            
            # Update previous states
            self.previous_states[zone_name]['active'] = is_active
            self.previous_states[zone_name]['boiler'] = boiler_on
            
            return transition_occurred
            
        except Exception as e:
            print(f"Error checking zone {zone_name}: {e}")
            return False
    
    def check_all_zones(self):
        """Check all zones for transitions"""
        try:
            zones = self.ember.get_zone_names()
            transitions = []
            
            for zone in zones:
                if self.check_zone_transition(zone):
                    transitions.append(zone)
            
            if transitions:
                self.save_state()
            
            return transitions
            
        except Exception as e:
            print(f"Error checking zones: {e}")
            return []
    
    def get_transition_summary(self):
        """Get summary of all transition counts"""
        summary = {}
        for zone, counts in self.transition_counts.items():
            summary[zone] = {
                'heating_cycles': counts['active_transitions'],
                'boiler_cycles': counts['boiler_transitions'],
                'last_heating_on': counts.get('last_active_transition'),
                'last_boiler_on': counts.get('last_boiler_transition')
            }
        return summary
    
    def monitor_continuous(self, check_interval=60):
        """
        Continuously monitor for transitions
        check_interval: seconds between checks
        """
        print(f"🎯 Starting heating transition monitor (checking every {check_interval}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                transitions = self.check_all_zones()
                
                if not transitions:
                    # Show current status
                    now = datetime.datetime.now().strftime("%H:%M:%S")
                    zones = self.ember.get_zone_names()
                    status = []
                    for zone in zones:
                        try:
                            active = self.ember.is_zone_active(zone)
                            boiler = self.ember.is_zone_boiler_on(zone)
                            temp = self.ember.get_zone_temperature(zone)
                            target = self.ember.get_zone_target_temperature(zone)
                            status.append(f"{zone}: {'🔥' if active else '❄️'} {temp}°C→{target}°C")
                        except:
                            status.append(f"{zone}: ❌ Error")
                    print(f"[{now}] {' | '.join(status)}")
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            self.save_state()
            print("📊 Final transition summary:")
            summary = self.get_transition_summary()
            for zone, stats in summary.items():
                print(f"  {zone}: {stats['heating_cycles']} heating cycles, {stats['boiler_cycles']} boiler cycles")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 heating_counter.py monitor          # Continuous monitoring")
        print("  python3 heating_counter.py check            # Single check")
        print("  python3 heating_counter.py summary          # Show summary")
        print("  python3 heating_counter.py reset            # Reset counters")
        print("\nSet credentials with environment variables:")
        print("  export EPH_EMAIL='your-email@example.com'")
        print("  export EPH_PASSWORD='your-password'")
        return
    
    email = os.environ.get('EPH_EMAIL')
    password = os.environ.get('EPH_PASSWORD')
    
    if not email or not password:
        print("❌ Please set EPH_EMAIL and EPH_PASSWORD environment variables")
        return
    
    counter = HeatingTransitionCounter(email, password)
    command = sys.argv[1]
    
    if command == 'monitor':
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        counter.monitor_continuous(interval)
    
    elif command == 'check':
        transitions = counter.check_all_zones()
        if transitions:
            print(f"✅ Transitions detected in: {', '.join(transitions)}")
        else:
            print("ℹ️ No transitions detected")
    
    elif command == 'summary':
        summary = counter.get_transition_summary()
        print("📊 Heating Transition Summary:")
        for zone, stats in summary.items():
            print(f"\n🏠 {zone}:")
            print(f"   Heating Cycles: {stats['heating_cycles']}")
            print(f"   Boiler Cycles: {stats['boiler_cycles']}")
            if stats['last_heating_on']:
                print(f"   Last Heating On: {stats['last_heating_on']}")
            if stats['last_boiler_on']:
                print(f"   Last Boiler On: {stats['last_boiler_on']}")
    
    elif command == 'reset':
        confirm = input("⚠️ Reset all counters? (y/N): ")
        if confirm.lower() == 'y':
            counter.transition_counts = {}
            counter.previous_states = {}
            counter.save_state()
            print("✅ Counters reset")
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == '__main__':
    main()