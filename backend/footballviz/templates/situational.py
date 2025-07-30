"""
FootballViz Situational Analysis Templates

Templates for analyzing critical game situations:
- Red zone, goal line, third down performance
- Momentum shift analysis
- Critical decision points
"""

from typing import Dict, List, Any, Optional
import numpy as np

from ..charts.base import FootballChart
from ..core.colors import PerformanceColors


class CriticalSituations(FootballChart):
    """
    Analysis of performance in critical game situations
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            width=14,
            height=8,
            title="Critical Situations Analysis",
            **kwargs
        )
    
    def plot(self, data: Dict[str, Any], **kwargs) -> 'CriticalSituations':
        """
        Create critical situations analysis chart
        
        Args:
            data: Situational performance data
            **kwargs: Additional plotting parameters
        """
        self.data = data
        self.create_figure()
        
        # Placeholder data for critical situations
        situations = {
            'Red Zone (Attempts: 8)': {'success_rate': 75, 'attempts': 8, 'successes': 6},
            '3rd Down (Attempts: 12)': {'success_rate': 42, 'attempts': 12, 'successes': 5},
            'Goal Line (Attempts: 3)': {'success_rate': 100, 'attempts': 3, 'successes': 3},
            '4th Down (Attempts: 2)': {'success_rate': 50, 'attempts': 2, 'successes': 1},
            'Two-Minute (Attempts: 4)': {'success_rate': 25, 'attempts': 4, 'successes': 1}
        }
        
        labels = list(situations.keys())
        success_rates = [data['success_rate'] for data in situations.values()]
        colors = [PerformanceColors.get_performance_color(rate) for rate in success_rates]
        
        bars = self.ax.barh(labels, success_rates, color=colors, alpha=0.85)
        
        # Add success/attempt labels
        for i, (bar, situation_data) in enumerate(zip(bars, situations.values())):
            width = bar.get_width()
            successes = situation_data['successes']
            attempts = situation_data['attempts']
            self.ax.text(width + 2, bar.get_y() + bar.get_height()/2,
                       f'{successes}/{attempts} ({width:.0f}%)', 
                       ha='left', va='center',
                       **self.theme.font_manager.get_text_properties('data_labels',
                                                                   self.theme.config.primary_text_color))
        
        self.ax.set_xlabel('Success Rate (%)')
        self.ax.set_title('Performance in Critical Situations')
        self.ax.set_xlim(0, 110)  # Extra space for labels
        
        # Add league average reference line
        league_avg = 50
        self.add_reference_line(league_avg, 'vertical', 'League Avg', 
                              PerformanceColors.NEUTRAL, '--')
        
        self.optimize_layout()
        return self


class MomentumAnalysis(FootballChart):
    """
    Analysis of momentum shifts throughout the game
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            width=14,
            height=8,
            title="Game Momentum Analysis",
            **kwargs
        )
    
    def plot(self, data: Dict[str, Any], **kwargs) -> 'MomentumAnalysis':
        """
        Create momentum analysis chart
        
        Args:
            data: Game timeline data with scoring and key events
            **kwargs: Additional plotting parameters
        """
        self.data = data
        self.create_figure()
        
        # Placeholder timeline data
        timeline = {
            '1st Q': {'score_diff': 7, 'momentum': 60},
            '2nd Q': {'score_diff': 14, 'momentum': 75},
            '3rd Q': {'score_diff': 3, 'momentum': 45},
            '4th Q': {'score_diff': 10, 'momentum': 65}
        }
        
        quarters = list(timeline.keys())
        score_diffs = [data['score_diff'] for data in timeline.values()]
        momentum_scores = [data['momentum'] for data in timeline.values()]
        
        # Create dual-axis chart
        ax2 = self.ax.twinx()
        
        # Score differential bars
        color_map = [PerformanceColors.GOOD if diff > 0 else 
                    PerformanceColors.CONCERN if diff < 0 else 
                    PerformanceColors.NEUTRAL for diff in score_diffs]
        
        bars = self.ax.bar(quarters, score_diffs, color=color_map, alpha=0.7, label='Score Differential')
        
        # Momentum line
        line = ax2.plot(quarters, momentum_scores, color=PerformanceColors.EMPHASIS,
                       marker='o', linewidth=3, markersize=8, label='Momentum Score')
        
        # Add horizontal line at 50% momentum
        ax2.axhline(y=50, color=PerformanceColors.NEUTRAL, linestyle='--', alpha=0.5)
        
        self.ax.set_ylabel('Score Differential', color=self.theme.config.team_primary)
        ax2.set_ylabel('Momentum Score (%)', color=PerformanceColors.EMPHASIS)
        self.ax.set_title('Score Differential and Momentum by Quarter')
        
        # Color-code the y-axis labels
        self.ax.tick_params(axis='y', labelcolor=self.theme.config.team_primary)
        ax2.tick_params(axis='y', labelcolor=PerformanceColors.EMPHASIS)
        
        # Add annotations for key events
        key_events = [
            (1, 'Opening TD'),
            (2, 'Turnover Recovery'),
            (3, 'Missed FG'),
            (4, 'Game-winning Drive')
        ]
        
        for quarter_idx, event in key_events:
            if quarter_idx <= len(quarters):
                self.ax.annotate(event, 
                               xy=(quarter_idx-1, score_diffs[quarter_idx-1]),
                               xytext=(10, 10), textcoords='offset points',
                               bbox=dict(boxstyle='round,pad=0.3', 
                                       facecolor=PerformanceColors.EMPHASIS, alpha=0.7),
                               arrowprops=dict(arrowstyle='->', color=PerformanceColors.EMPHASIS),
                               **self.theme.font_manager.get_text_properties('annotations',
                                                                           'white'))
        
        self.optimize_layout()
        return self