#!/usr/bin/env python3
"""
Test script to analyze your actual EPH heating program data
"""

import json
from typing import Dict, List, Any, Optional

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
    
    def print_program_analysis(self, program_id: int):
        """Print a detailed analysis of a program"""
        print(f"\n=== PROGRAM {program_id} ANALYSIS ===")
        
        summary = self.get_program_summary(program_id)
        if 'error' in summary:
            print(summary['error'])
            return
        
        print(f"Total Steps: {summary['total_steps']}")
        if summary['temperature_range']['min']:
            print(f"Temperature Range: {summary['temperature_range']['min']/10:.1f}°C - {summary['temperature_range']['max']/10:.1f}°C")
            print(f"Average Temperature: {summary['temperature_range']['average']/10:.1f}°C")
        if summary['time_range']['total']:
            print(f"Total Time: {summary['time_range']['total']} minutes")
        
        print("\nProgram Steps:")
        for step in summary['sequence']:
            temp = f"{step['temperature']/10:.1f}°C" if step['temperature'] else "N/A"
            time = f"{step['time']} min" if step['time'] else "N/A"
            print(f"  Step {step['step']}: {temp} for {time}")
    
    def analyze_all_programs(self) -> Dict[int, List[Dict[str, Any]]]:
        """Analyze all available programs"""
        programs = {}
        
        if 'programs' in self.program_data:
            for program_id in self.program_data['programs'].keys():
                if isinstance(program_id, int):
                    programs[program_id] = self.extract_program_sequence(program_id)
        
        return programs

# Your actual program data (truncated version for analysis)
program_data = {
    "programs": {
        1: {
            "endTime": None,
            "id": "28a8b900-38cc-495b-b4fe-0e4e8d7659aa",
            "startTime": None,
            "temperature": 175,
            "time": 40,
            "Prev": {
                "endTime": None,
                "id": "18a8b900-38cc-495b-b4fe-0e4e8d7659aa",
                "startTime": None,
                "temperature": 175,
                "time": 140,
                "Count": 6
            },
            "Next": {
                "endTime": None,
                "id": "38a8b900-38cc-495b-b4fe-0e4e8d7659aa", 
                "startTime": None,
                "temperature": 185,
                "time": 60,
                "Prev": {
                    "endTime": None,
                    "id": "28a8b900-38cc-495b-b4fe-0e4e8d7659aa",
                    "startTime": None,
                    "temperature": 175,
                    "time": 40,
                    "Count": 1
                },
                "Next": {
                    "endTime": None,
                    "id": "48a8b900-38cc-495b-b4fe-0e4e8d7659aa",
                    "startTime": None,
                    "temperature": 200,
                    "time": 10,
                    "Count": 3
                },
                "Count": 2
            },
            "Count": 1
        },
        2: {
            "endTime": None,
            "id": "208b900-38cc-495b-b4fe-0e4e8d7659bb",
            "startTime": None,
            "temperature": 200,
            "time": 50,
            "Count": 1
        }
    }
}

def main():
    """Analyze the EPH heating program data"""
    print("EPH Heating Program Data Analysis")
    print("=" * 40)
    
    analyzer = HeatingProgramAnalyzer(program_data)
    
    # Analyze all available programs
    all_programs = analyzer.analyze_all_programs()
    print(f"Found {len(all_programs)} programs")
    
    # Detailed analysis of each program
    for program_id in all_programs.keys():
        analyzer.print_program_analysis(program_id)
    
    # Show the structure understanding
    print("\n=== STRUCTURE UNDERSTANDING ===")
    print("The EPH heating system uses circular linked lists for programs:")
    print("- Each program step has 'Prev' and 'Next' pointers")
    print("- Each step has temperature (1/10th degrees), time (minutes), and unique ID")
    print("- 'Count' appears to track position in the sequence")
    print("- Programs can have complex multi-step heating cycles")
    
    print("\n=== HEATING INTERPRETATION ===")
    for program_id in [1, 2]:
        sequence = analyzer.extract_program_sequence(program_id)
        if sequence:
            print(f"\nProgram {program_id} heating schedule:")
            total_time = 0
            for step in sequence:
                temp_celsius = step['temperature'] / 10 if step['temperature'] else 0
                time_min = step['time'] if step['time'] else 0
                total_time += time_min
                print(f"  {temp_celsius:.1f}°C for {time_min} minutes (total: {total_time} min)")

if __name__ == "__main__":
    main()