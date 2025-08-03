#!/usr/bin/env python3

"""Test script for statistical chart generation"""

import sys
import os
sys.path.append('.')

from footballviz.charts.statistical import create_statistical_chart

# Sample test data
test_plays = [
    {'play_id': 1, 'down': 1, 'distance': 10, 'yard_line': 25, 'formation': 'I-Form', 
     'play_type': 'Run', 'yards_gained': 4, 'points_scored': 0, 'unit': 'O'},
    {'play_id': 2, 'down': 2, 'distance': 6, 'yard_line': 29, 'formation': 'Shotgun', 
     'play_type': 'Pass', 'yards_gained': 8, 'points_scored': 0, 'unit': 'O'},
    {'play_id': 3, 'down': 1, 'distance': 10, 'yard_line': 37, 'formation': 'Singleback', 
     'play_type': 'Pass', 'yards_gained': 25, 'points_scored': 0, 'unit': 'O'},
    {'play_id': 4, 'down': 1, 'distance': 10, 'yard_line': 62, 'formation': 'Shotgun', 
     'play_type': 'Pass', 'yards_gained': 9, 'points_scored': 0, 'unit': 'O'},
    {'play_id': 5, 'down': 2, 'distance': 1, 'yard_line': 71, 'formation': 'Goal Line', 
     'play_type': 'Run', 'yards_gained': 0, 'points_scored': 0, 'unit': 'O'},
]

def test_chart_generation():
    """Test chart generation"""
    try:
        print("Testing chart generation...")
        
        # Test distribution chart
        chart_data = create_statistical_chart('distribution', test_plays)
        print(f"✅ Distribution chart generated, length: {len(chart_data)} characters")
        
        # Test formation comparison
        chart_data = create_statistical_chart('formation_comparison', test_plays)
        print(f"✅ Formation comparison chart generated, length: {len(chart_data)} characters")
        
        print("✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_chart_generation()
    sys.exit(0 if success else 1)