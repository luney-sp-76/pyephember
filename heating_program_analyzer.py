#!/usr/bin/env python3
"""
Heating Program Data Analyzer
Analyzes the complex heating program data structure from EPH heating systems
"""

import json
from typing import Dict, List, Any, Optional
from collections import deque

class HeatingProgramAnalyzer:
    """Analyzes EPH heating program data structures"""
    
    def __init__(self, program_data: Dict[str, Any]):
        """Initialize with program data"""
        self.program_data = program_data
        self.analysis = {}
    
    def extract_program_sequence(self, program_id: int, max_steps: int = 20) -> List[Dict[str, Any]]:
        """
        Extract a linear sequence from a circular linked list program
        
        Args:
            program_id: The program ID to extract (1-6 typically)
            max_steps: Maximum steps to prevent infinite loops
            
        Returns:
            List of program steps with temperature, time, and other data
        """
        if 'programs' not in self.program_data or program_id not in self.program_data['programs']:
            return []
        
        sequence = []
        current = self.program_data['programs'][program_id]
        visited_ids = set()
        
        for step in range(max_steps):
            if current['id'] in visited_ids:
                # We've completed the cycle
                break
                
            step_data = {
                'step': step + 1,
                'id': current['id'],
                'temperature': current.get('temperature'),
                'time': current.get('time'),
                'count': current.get('Count'),
                'start_time': current.get('startTime'),
                'end_time': current.get('endTime')
            }
            
            sequence.append(step_data)
            visited_ids.add(current['id'])
            
            # Move to next step
            if 'Next' in current and isinstance(current['Next'], dict):
                current = current['Next']
            else:
                break
        
        return sequence
    
    def analyze_all_programs(self) -> Dict[int, List[Dict[str, Any]]]:
        """Analyze all available programs"""
        programs = {}
        
        if 'programs' in self.program_data:
            for program_id in self.program_data['programs'].keys():
                if isinstance(program_id, int):
                    programs[program_id] = self.extract_program_sequence(program_id)
        
        return programs
    
    def get_program_summary(self, program_id: int) -> Dict[str, Any]:
        """Get a summary of a specific program"""
        sequence = self.extract_program_sequence(program_id)
        
        if not sequence:
            return {"error": f"No data found for program {program_id}"}
        
        temperatures = [step['temperature'] for step in sequence if step['temperature']]
        times = [step['time'] for step in sequence if step['time']]
        
        summary = {
            'program_id': program_id,
            'total_steps': len(sequence),
            'temperature_range': {
                'min': min(temperatures) if temperatures else None,
                'max': max(temperatures) if temperatures else None,
                'average': sum(temperatures) / len(temperatures) if temperatures else None
            },
            'time_range': {
                'min': min(times) if times else None,
                'max': max(times) if times else None,
                'total': sum(times) if times else None
            },
            'sequence': sequence[:6]  # First 6 steps for preview
        }
        
        return summary
    
    def detect_heating_cycles(self, program_id: int) -> List[Dict[str, Any]]:
        """
        Detect heating cycles in the program data
        A heating cycle might be defined as temperature changes over time
        """
        sequence = self.extract_program_sequence(program_id)
        cycles = []
        
        if len(sequence) < 2:
            return cycles
        
        current_cycle = {'start_temp': sequence[0]['temperature'], 'steps': [sequence[0]]}
        
        for i in range(1, len(sequence)):
            current_step = sequence[i]
            prev_step = sequence[i-1]
            
            # If temperature changes significantly, consider it a new cycle
            temp_diff = abs(current_step['temperature'] - prev_step['temperature'])
            
            if temp_diff > 10:  # 10 degree threshold
                # End current cycle
                current_cycle['end_temp'] = prev_step['temperature']
                current_cycle['duration'] = sum(step['time'] for step in current_cycle['steps'] if step['time'])
                cycles.append(current_cycle)
                
                # Start new cycle
                current_cycle = {'start_temp': current_step['temperature'], 'steps': [current_step]}
            else:
                current_cycle['steps'].append(current_step)
        
        # Add the last cycle
        if current_cycle['steps']:
            current_cycle['end_temp'] = current_cycle['steps'][-1]['temperature']
            current_cycle['duration'] = sum(step['time'] for step in current_cycle['steps'] if step['time'])
            cycles.append(current_cycle)
        
        return cycles
    
    def print_program_analysis(self, program_id: int):
        """Print a detailed analysis of a program"""
        print(f"\n=== PROGRAM {program_id} ANALYSIS ===")
        
        summary = self.get_program_summary(program_id)
        if 'error' in summary:
            print(summary['error'])
            return
        
        print(f"Total Steps: {summary['total_steps']}")
        print(f"Temperature Range: {summary['temperature_range']['min']}°C - {summary['temperature_range']['max']}°C")
        print(f"Average Temperature: {summary['temperature_range']['average']:.1f}°C")
        print(f"Total Time: {summary['time_range']['total']} minutes")
        
        print("\nFirst 6 Steps:")
        for step in summary['sequence']:
            print(f"  Step {step['step']}: {step['temperature']}°C for {step['time']} minutes")
        
        cycles = self.detect_heating_cycles(program_id)
        print(f"\nDetected {len(cycles)} heating cycles:")
        for i, cycle in enumerate(cycles):
            print(f"  Cycle {i+1}: {cycle['start_temp']}°C → {cycle['end_temp']}°C ({cycle['duration']} min)")

def main():
    """Example usage of the analyzer"""
    # This would be filled with your actual program data
    sample_data = {
        "programs": {
            1: {
                "id": "sample",
                "temperature": 175,
                "time": 40,
                "Next": {
                    "id": "sample2", 
                    "temperature": 185,
                    "time": 60,
                    "Next": None
                }
            }
        }
    }
    
    analyzer = HeatingProgramAnalyzer(sample_data)
    analyzer.print_program_analysis(1)

if __name__ == "__main__":
    main()