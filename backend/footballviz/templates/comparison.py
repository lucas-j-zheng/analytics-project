"""
FootballViz Comparison Templates

Chart templates for comparing performance across different contexts:
- Team vs opponent comparisons  
- Historical performance comparisons
- Game review and analysis
"""

from typing import Dict, List, Any, Optional
import numpy as np

from ..charts.base import FootballChart
from ..core.colors import PerformanceColors, COMPARISON_PALETTE


class PerformanceComparison(FootballChart):
    """
    Side-by-side performance comparison chart
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            width=14,
            height=8,
            title="Performance Comparison",
            **kwargs
        )
    
    def plot(self, 
             data: Dict[str, Any],
             comparison_data: Dict[str, Any],
             labels: tuple = ("Team", "Opponent"),
             **kwargs) -> 'PerformanceComparison':
        """
        Create performance comparison chart
        
        Args:
            data: Primary dataset
            comparison_data: Comparison dataset
            labels: Labels for the two datasets
            **kwargs: Additional plotting parameters
        """
        self.data = data
        self.create_figure()
        
        # Extract key metrics for comparison
        metrics = ['Yards/Play', 'Success Rate', 'Red Zone %', '3rd Down %', 'Explosive Plays']
        
        # Placeholder values - in real implementation, extract from processed data
        team_values = [5.2, 68, 75, 42, 8]
        opponent_values = [4.8, 62, 68, 38, 6]
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = self.ax.bar(x - width/2, team_values, width, 
                           label=labels[0], color=self.theme.config.team_primary, alpha=0.8)
        bars2 = self.ax.bar(x + width/2, opponent_values, width,
                           label=labels[1], color=self.theme.config.opponent_color, alpha=0.8)
        
        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{height:.1f}', ha='center', va='bottom',
                           **self.theme.font_manager.get_text_properties('data_labels',
                                                                       self.theme.config.primary_text_color))
        
        self.ax.set_xlabel('Performance Metrics')
        self.ax.set_ylabel('Value')
        self.ax.set_title(f'{labels[0]} vs {labels[1]} Comparison')
        self.ax.set_xticks(x)
        self.ax.set_xticklabels(metrics)
        self.ax.legend()
        
        self.optimize_layout()
        return self


class GameReview(FootballChart):
    """
    Post-game review and analysis chart
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            width=16,
            height=10,
            title="Game Review Analysis",
            **kwargs
        )
    
    def plot(self, data: Dict[str, Any], **kwargs) -> 'GameReview':
        """
        Create comprehensive game review chart
        
        Args:
            data: Game performance data
            **kwargs: Additional plotting parameters
        """
        self.data = data
        self.create_figure()
        
        # Create multi-panel layout
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Quarter-by-quarter performance
        ax1 = self.fig.add_subplot(gs[0, 0])
        self._plot_quarter_performance(ax1)
        
        # Drive outcomes
        ax2 = self.fig.add_subplot(gs[0, 1])
        self._plot_drive_outcomes(ax2)
        
        # Key situations
        ax3 = self.fig.add_subplot(gs[1, 0])
        self._plot_key_situations(ax3)
        
        # Performance vs expectation
        ax4 = self.fig.add_subplot(gs[1, 1])
        self._plot_vs_expectation(ax4)
        
        # Apply theme to all subplots
        for ax in [ax1, ax2, ax3, ax4]:
            self.theme.apply_to_figure(self.fig, ax)
        
        self.optimize_layout()
        return self
    
    def _plot_quarter_performance(self, ax):
        """Plot performance by quarter"""
        quarters = ['Q1', 'Q2', 'Q3', 'Q4']
        points = [7, 14, 3, 10]  # Placeholder data
        yards = [125, 180, 85, 160]  # Placeholder data
        
        ax2 = ax.twinx()
        
        bars = ax.bar(quarters, points, color=self.theme.config.team_primary, alpha=0.8, label='Points')
        line = ax2.plot(quarters, yards, color=PerformanceColors.EMPHASIS, 
                       marker='o', linewidth=3, label='Yards')
        
        ax.set_ylabel('Points', color=self.theme.config.team_primary)
        ax2.set_ylabel('Yards', color=PerformanceColors.EMPHASIS)
        ax.set_title('Quarter-by-Quarter Performance')
        
        ax.tick_params(axis='y', labelcolor=self.theme.config.team_primary)
        ax2.tick_params(axis='y', labelcolor=PerformanceColors.EMPHASIS)
    
    def _plot_drive_outcomes(self, ax):
        """Plot drive outcome distribution"""
        outcomes = ['Touchdown', 'Field Goal', 'Punt', 'Turnover', 'Other']
        counts = [4, 2, 6, 1, 1]  # Placeholder data
        
        colors = [PerformanceColors.ELITE, PerformanceColors.GOOD, 
                 PerformanceColors.AVERAGE, PerformanceColors.CONCERN,
                 PerformanceColors.NEUTRAL]
        
        wedges, texts, autotexts = ax.pie(counts, labels=outcomes, colors=colors,
                                         autopct='%1.0f%%', startangle=90)
        
        ax.set_title('Drive Outcomes')
        
        for text in texts:
            text.set_color(self.theme.config.secondary_text_color)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    def _plot_key_situations(self, ax):
        """Plot key situational performance"""
        situations = ['Red Zone', '3rd Down', 'Goal Line', '4th Down']
        attempts = [8, 12, 3, 2]  # Placeholder data
        successes = [6, 5, 3, 1]  # Placeholder data
        
        success_rates = [(s/a*100) if a > 0 else 0 for s, a in zip(successes, attempts)]
        colors = [PerformanceColors.get_performance_color(rate) for rate in success_rates]
        
        bars = ax.bar(situations, success_rates, color=colors, alpha=0.85)
        
        # Add attempt counts as annotations
        for i, (bar, attempts_count) in enumerate(zip(bars, attempts)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{successes[i]}/{attempts_count}', ha='center', va='bottom',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Key Situations Performance')
        ax.set_ylim(0, 100)
    
    def _plot_vs_expectation(self, ax):
        """Plot actual vs expected performance"""
        metrics = ['Points', 'Yards', 'Turnovers']
        actual = [34, 550, 1]  # Placeholder data
        expected = [28, 480, 2]  # Placeholder data
        
        x = np.arange(len(metrics))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, actual, width, label='Actual', 
                      color=self.theme.config.team_primary, alpha=0.8)
        bars2 = ax.bar(x + width/2, expected, width, label='Expected',
                      color=PerformanceColors.NEUTRAL, alpha=0.8)
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Value')
        ax.set_title('Actual vs Expected Performance')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()