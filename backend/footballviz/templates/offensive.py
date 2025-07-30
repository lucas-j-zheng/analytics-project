"""
FootballViz Offensive Analytics Templates

Specialized chart templates for offensive performance analysis:
- Offensive efficiency metrics (red zone %, 3rd down %, yards per play)
- Personnel/formation effectiveness analysis
- Field position impact visualization
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from ..charts.base import FootballChart
from ..utils.data_processor import FootballDataProcessor, EfficiencyCalculator
from ..core.colors import PerformanceColors, OFFENSIVE_PALETTE


class OffensiveEfficiency(FootballChart):
    """
    Comprehensive offensive efficiency analysis chart
    
    Displays:
    - Red zone efficiency
    - Third down conversion rate
    - Average yards per play
    - Success rate by situation
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            width=14,
            height=10,
            title="Offensive Efficiency Analysis",
            **kwargs
        )
        self.processor = FootballDataProcessor()
    
    def plot(self, 
             data: Dict[str, Any], 
             comparison_data: Optional[Dict[str, Any]] = None,
             show_league_average: bool = True,
             **kwargs) -> 'OffensiveEfficiency':
        """
        Create offensive efficiency analysis chart
        
        Args:
            data: Processed play data
            comparison_data: Optional comparison data (opponent/previous game)
            show_league_average: Whether to show league average reference lines
            **kwargs: Additional plotting parameters
        """
        self.data = data
        self.create_figure()
        
        # Create subplots for different efficiency metrics
        gs = self.fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # Main efficiency metrics (top row, spans 2 columns)
        ax_main = self.fig.add_subplot(gs[0, :2])
        self._plot_main_efficiency_metrics(ax_main, data, comparison_data)
        
        # Situational breakdown (top right)
        ax_situational = self.fig.add_subplot(gs[0, 2])
        self._plot_situational_efficiency(ax_situational, data)
        
        # Down and distance analysis (bottom left)
        ax_down_distance = self.fig.add_subplot(gs[1, 0])
        self._plot_down_distance_efficiency(ax_down_distance, data)
        
        # Formation efficiency (bottom center)
        ax_formations = self.fig.add_subplot(gs[1, 1])
        self._plot_formation_efficiency(ax_formations, data)
        
        # Efficiency trends (bottom right)
        ax_trends = self.fig.add_subplot(gs[1, 2])
        self._plot_efficiency_trends(ax_trends, data)
        
        # Apply theme to all subplots
        for ax in [ax_main, ax_situational, ax_down_distance, ax_formations, ax_trends]:
            self.theme.apply_to_figure(self.fig, ax)
        
        self.optimize_layout()
        return self
    
    def _plot_main_efficiency_metrics(self, ax, data: Dict[str, Any], comparison_data: Optional[Dict[str, Any]]):
        """Plot main efficiency metrics bar chart"""
        
        situational = data.get('situational', {})
        summary = data.get('summary')
        
        # Define metrics
        metrics = {
            'Red Zone\nEfficiency': situational.get('red_zone', {}).get('success_rate', 0),
            '3rd Down\nConversion': situational.get('third_down', {}).get('success_rate', 0),
            'Goal Line\nEfficiency': situational.get('goal_line', {}).get('success_rate', 0),
            'Short Yardage\nSuccess': situational.get('short_yardage', {}).get('success_rate', 0),
            'Overall\nSuccess Rate': summary.success_rate if summary else 0
        }
        
        x_pos = np.arange(len(metrics))
        values = list(metrics.values())
        labels = list(metrics.keys())
        
        # Color bars based on performance
        colors = [PerformanceColors.get_performance_color(v) for v in values]
        
        bars = ax.bar(x_pos, values, color=colors, alpha=0.85, edgecolor='white', linewidth=1.5)
        
        # Add comparison data if provided
        if comparison_data:
            comp_situational = comparison_data.get('situational', {})
            comp_summary = comparison_data.get('summary')
            
            comp_values = [
                comp_situational.get('red_zone', {}).get('success_rate', 0),
                comp_situational.get('third_down', {}).get('success_rate', 0),
                comp_situational.get('goal_line', {}).get('success_rate', 0),
                comp_situational.get('short_yardage', {}).get('success_rate', 0),
                comp_summary.success_rate if comp_summary else 0
            ]
            
            # Add comparison bars (slightly offset)
            x_offset = 0.25
            comp_bars = ax.bar(x_pos + x_offset, comp_values, 
                             width=0.5, color=self.theme.config.opponent_color, 
                             alpha=0.7, label='Opponent')
        
        # Add data labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{value:.1f}%', ha='center', va='bottom',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        # Styling
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels)
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Key Offensive Efficiency Metrics', 
                    **self.theme.font_manager.get_text_properties('subtitle',
                                                                self.theme.config.primary_text_color))
        
        # Add league average reference lines
        league_averages = {'red_zone': 55, 'third_down': 40, 'goal_line': 65, 'short_yardage': 70, 'overall': 45}
        for i, avg in enumerate(league_averages.values()):
            ax.axhline(y=avg, color=PerformanceColors.NEUTRAL, linestyle='--', alpha=0.5, linewidth=1)
        
        ax.set_ylim(0, 100)
        self.format_percentage_axis(ax, 'y')
        
        if comparison_data:
            ax.legend()
    
    def _plot_situational_efficiency(self, ax, data: Dict[str, Any]):
        """Plot situational efficiency radar/polar chart"""
        
        situational = data.get('situational', {})
        
        # Situational categories
        situations = ['Red Zone', '3rd Down', 'Goal Line', 'Short Yardage', '4th Down']
        values = [
            situational.get('red_zone', {}).get('success_rate', 0),
            situational.get('third_down', {}).get('success_rate', 0),
            situational.get('goal_line', {}).get('success_rate', 0),
            situational.get('short_yardage', {}).get('success_rate', 0),
            situational.get('fourth_down', {}).get('success_rate', 0)
        ]
        
        # Create simple bar chart (radar would be more complex)
        y_pos = np.arange(len(situations))
        colors = [PerformanceColors.get_performance_color(v) for v in values]
        
        bars = ax.barh(y_pos, values, color=colors, alpha=0.85)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, values)):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                   f'{value:.1f}%', ha='left', va='center',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        ax.set_yticks(y_pos)
        ax.set_yticklabels(situations)
        ax.set_xlabel('Success Rate (%)')
        ax.set_title('Situational Performance',
                    **self.theme.font_manager.get_text_properties('subtitle',
                                                                self.theme.config.primary_text_color))
        ax.set_xlim(0, 100)
    
    def _plot_down_distance_efficiency(self, ax, data: Dict[str, Any]):
        """Plot down and distance efficiency"""
        
        down_distance_data = data.get('down_distance', {})
        
        if not down_distance_data:
            ax.text(0.5, 0.5, 'No down/distance data available', 
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        downs = list(down_distance_data.keys())
        success_rates = [stats.get('success_rate', 0) for stats in down_distance_data.values()]
        avg_yards = [stats.get('avg_yards', 0) for stats in down_distance_data.values()]
        
        # Create dual-axis chart
        ax2 = ax.twinx()
        
        x_pos = np.arange(len(downs))
        
        # Success rate bars
        bars1 = ax.bar(x_pos - 0.2, success_rates, 0.4, 
                      color=PerformanceColors.GOOD, alpha=0.8, label='Success Rate')
        
        # Average yards line
        line = ax2.plot(x_pos, avg_yards, color=PerformanceColors.EMPHASIS, 
                       marker='o', linewidth=3, markersize=8, label='Avg Yards')
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(downs)
        ax.set_ylabel('Success Rate (%)', color=PerformanceColors.GOOD)
        ax2.set_ylabel('Average Yards', color=PerformanceColors.EMPHASIS)
        ax.set_title('Down & Distance Analysis',
                    **self.theme.font_manager.get_text_properties('subtitle',
                                                                self.theme.config.primary_text_color))
        
        # Color-code the y-axis labels
        ax.tick_params(axis='y', labelcolor=PerformanceColors.GOOD)
        ax2.tick_params(axis='y', labelcolor=PerformanceColors.EMPHASIS)
    
    def _plot_formation_efficiency(self, ax, data: Dict[str, Any]):
        """Plot formation efficiency analysis"""
        
        formations_data = data.get('formations', {})
        
        if not formations_data:
            ax.text(0.5, 0.5, 'No formation data available',
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Get top 5 most used formations
        sorted_formations = sorted(formations_data.items(), 
                                 key=lambda x: x[1].get('count', 0), reverse=True)[:5]
        
        formations = [f[0] for f in sorted_formations]
        efficiencies = [f[1].get('success_rate', 0) for f in sorted_formations]
        counts = [f[1].get('count', 0) for f in sorted_formations]
        
        # Bubble chart: x=formation, y=efficiency, size=usage
        x_pos = np.arange(len(formations))
        
        # Normalize bubble sizes
        max_count = max(counts) if counts else 1
        bubble_sizes = [(c / max_count) * 1000 + 100 for c in counts]
        
        colors = [PerformanceColors.get_performance_color(e) for e in efficiencies]
        
        scatter = ax.scatter(x_pos, efficiencies, s=bubble_sizes, c=colors, 
                           alpha=0.7, edgecolors='white', linewidth=2)
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(formations, rotation=45, ha='right')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Formation Efficiency\n(Bubble size = Usage)',
                    **self.theme.font_manager.get_text_properties('subtitle',
                                                                self.theme.config.primary_text_color))
        
        # Add count labels
        for i, (x, y, count) in enumerate(zip(x_pos, efficiencies, counts)):
            ax.text(x, y, str(count), ha='center', va='center',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.background_color))
    
    def _plot_efficiency_trends(self, ax, data: Dict[str, Any]):
        """Plot efficiency trends (would need game-by-game data)"""
        
        # Placeholder for trend analysis
        # In real implementation, would show efficiency across games
        
        summary = data.get('summary')
        if not summary:
            ax.text(0.5, 0.5, 'Insufficient data for trends',
                   ha='center', va='center', transform=ax.transAxes)
            return
        
        # Show efficiency distribution as histogram
        # This is a simplified version - real implementation would use time series
        
        metrics = [
            summary.success_rate,
            summary.avg_yards_per_play * 10,  # Scale for visibility
            (summary.explosive_plays / summary.total_plays * 100) if summary.total_plays > 0 else 0
        ]
        
        metric_names = ['Success\nRate', 'Yards/Play\n(x10)', 'Explosive\nPlay %']
        
        bars = ax.bar(metric_names, metrics, 
                     color=[PerformanceColors.get_performance_color(m) for m in metrics],
                     alpha=0.8)
        
        # Add value labels
        for bar, value in zip(bars, metrics):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                   f'{value:.1f}', ha='center', va='bottom',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        ax.set_title('Performance Summary',
                    **self.theme.font_manager.get_text_properties('subtitle',
                                                                self.theme.config.primary_text_color))
        ax.set_ylabel('Value')


class PersonnelEffectiveness(FootballChart):
    """
    Personnel grouping and formation effectiveness analysis
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            width=12,
            height=8,
            title="Personnel & Formation Effectiveness",
            **kwargs
        )
    
    def plot(self, data: Dict[str, Any], **kwargs) -> 'PersonnelEffectiveness':
        """
        Create personnel effectiveness visualization
        
        Args:
            data: Processed play data with formation analysis
        """
        self.data = data
        self.create_figure()
        
        formations_data = data.get('formations', {})
        
        if not formations_data:
            self.ax.text(0.5, 0.5, 'No formation data available for analysis',
                        ha='center', va='center', transform=self.ax.transAxes,
                        **self.theme.font_manager.get_text_properties('title',
                                                                    self.theme.config.secondary_text_color))
            return self
        
        # Create matrix-style visualization
        formations = list(formations_data.keys())
        
        # Metrics: success rate, avg yards, usage frequency
        success_rates = [data.get('success_rate', 0) for data in formations_data.values()]
        avg_yards = [data.get('avg_yards', 0) for data in formations_data.values()]
        usage_counts = [data.get('count', 0) for data in formations_data.values()]
        
        # Create subplots
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Success rate by formation
        ax1 = self.fig.add_subplot(gs[0, 0])
        self._plot_formation_success_rates(ax1, formations, success_rates)
        
        # Average yards by formation
        ax2 = self.fig.add_subplot(gs[0, 1])
        self._plot_formation_yards(ax2, formations, avg_yards)
        
        # Usage frequency
        ax3 = self.fig.add_subplot(gs[1, 0])
        self._plot_formation_usage(ax3, formations, usage_counts)
        
        # Efficiency matrix
        ax4 = self.fig.add_subplot(gs[1, 1])
        self._plot_efficiency_matrix(ax4, formations, success_rates, avg_yards, usage_counts)
        
        # Apply theme to all subplots
        for ax in [ax1, ax2, ax3, ax4]:
            self.theme.apply_to_figure(self.fig, ax)
        
        self.optimize_layout()
        return self
    
    def _plot_formation_success_rates(self, ax, formations, success_rates):
        """Plot formation success rates"""
        colors = [PerformanceColors.get_performance_color(rate) for rate in success_rates]
        bars = ax.barh(formations, success_rates, color=colors, alpha=0.85)
        
        # Add value labels
        for bar, rate in zip(bars, success_rates):
            width = bar.get_width()
            ax.text(width + 1, bar.get_y() + bar.get_height()/2,
                   f'{rate:.1f}%', ha='left', va='center',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        ax.set_xlabel('Success Rate (%)')
        ax.set_title('Formation Success Rates')
        ax.set_xlim(0, 100)
    
    def _plot_formation_yards(self, ax, formations, avg_yards):
        """Plot average yards by formation"""
        colors = [PerformanceColors.get_performance_color(yards * 10) for yards in avg_yards]  # Scale for color
        bars = ax.barh(formations, avg_yards, color=colors, alpha=0.85)
        
        for bar, yards in zip(bars, avg_yards):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   f'{yards:.1f}', ha='left', va='center',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        ax.set_xlabel('Average Yards per Play')
        ax.set_title('Yards per Play by Formation')
    
    def _plot_formation_usage(self, ax, formations, usage_counts):
        """Plot formation usage frequency"""
        total_plays = sum(usage_counts)
        percentages = [(count / total_plays * 100) if total_plays > 0 else 0 for count in usage_counts]
        
        # Pie chart for usage
        colors = self.theme.get_color_palette('performance', len(formations))
        wedges, texts, autotexts = ax.pie(percentages, labels=formations, colors=colors,
                                         autopct='%1.1f%%', startangle=90)
        
        ax.set_title('Formation Usage Distribution')
        
        # Style the text
        for text in texts:
            text.set_color(self.theme.config.secondary_text_color)
            text.set_fontsize(self.theme.font_manager.get_font('annotations')['size'])
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    def _plot_efficiency_matrix(self, ax, formations, success_rates, avg_yards, usage_counts):
        """Plot efficiency matrix scatter plot"""
        # Normalize bubble sizes
        max_usage = max(usage_counts) if usage_counts else 1
        bubble_sizes = [(count / max_usage) * 1000 + 100 for count in usage_counts]
        
        colors = [PerformanceColors.get_performance_color(rate) for rate in success_rates]
        
        scatter = ax.scatter(avg_yards, success_rates, s=bubble_sizes, c=colors,
                           alpha=0.7, edgecolors='white', linewidth=2)
        
        # Add formation labels
        for i, formation in enumerate(formations):
            ax.annotate(formation, (avg_yards[i], success_rates[i]),
                       xytext=(5, 5), textcoords='offset points',
                       **self.theme.font_manager.get_text_properties('annotations',
                                                                   self.theme.config.tertiary_text_color))
        
        ax.set_xlabel('Average Yards per Play')
        ax.set_ylabel('Success Rate (%)')
        ax.set_title('Formation Efficiency Matrix\n(Bubble size = Usage frequency)')
        
        # Add quadrant lines
        avg_success = np.mean(success_rates) if success_rates else 50
        avg_yards_mean = np.mean(avg_yards) if avg_yards else 5
        
        ax.axhline(y=avg_success, color=PerformanceColors.NEUTRAL, linestyle='--', alpha=0.5)
        ax.axvline(x=avg_yards_mean, color=PerformanceColors.NEUTRAL, linestyle='--', alpha=0.5)


class FieldPositionImpact(FootballChart):
    """
    Field position impact on scoring and efficiency analysis
    """
    
    def __init__(self, **kwargs):
        super().__init__(
            width=14,
            height=8,
            title="Field Position Impact Analysis",
            **kwargs
        )
    
    def plot(self, data: Dict[str, Any], **kwargs) -> 'FieldPositionImpact':
        """
        Create field position impact visualization
        
        Args:
            data: Play data with field position information
        """
        self.data = data
        self.create_figure()
        
        # This would require play-by-play data with field position
        # For now, create a conceptual visualization
        
        # Create field zones
        field_zones = {
            'Own 1-20': {'scoring_rate': 5, 'avg_yards': 3.8, 'drives': 12},
            'Own 21-40': {'scoring_rate': 15, 'avg_yards': 4.2, 'drives': 18},
            'Own 41-50': {'scoring_rate': 25, 'avg_yards': 4.8, 'drives': 15},
            'Opp 50-31': {'scoring_rate': 45, 'avg_yards': 5.2, 'drives': 14},
            'Opp 30-21': {'scoring_rate': 65, 'avg_yards': 5.8, 'drives': 10},
            'Red Zone': {'scoring_rate': 85, 'avg_yards': 4.5, 'drives': 8}
        }
        
        zones = list(field_zones.keys())
        scoring_rates = [data['scoring_rate'] for data in field_zones.values()]
        avg_yards = [data['avg_yards'] for data in field_zones.values()]
        drive_counts = [data['drives'] for data in field_zones.values()]
        
        # Create subplots
        gs = self.fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
        
        # Scoring rate by field position
        ax1 = self.fig.add_subplot(gs[0, :])
        self._plot_field_position_scoring(ax1, zones, scoring_rates, drive_counts)
        
        # Efficiency by field zone
        ax2 = self.fig.add_subplot(gs[1, 0])
        self._plot_zone_efficiency(ax2, zones, avg_yards)
        
        # Field position heat map
        ax3 = self.fig.add_subplot(gs[1, 1])
        self._plot_field_heatmap(ax3, field_zones)
        
        # Apply theme
        for ax in [ax1, ax2, ax3]:
            self.theme.apply_to_figure(self.fig, ax)
        
        self.optimize_layout()
        return self
    
    def _plot_field_position_scoring(self, ax, zones, scoring_rates, drive_counts):
        """Plot scoring rates by field position"""
        x_pos = np.arange(len(zones))
        
        # Color bars based on scoring rate
        colors = [PerformanceColors.get_performance_color(rate) for rate in scoring_rates]
        bars = ax.bar(x_pos, scoring_rates, color=colors, alpha=0.85)
        
        # Add drive count annotations
        for i, (bar, rate, count) in enumerate(zip(bars, scoring_rates, drive_counts)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 2,
                   f'{rate}%\n({count} drives)', ha='center', va='bottom',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        ax.set_xticks(x_pos)
        ax.set_xticklabels(zones, rotation=45, ha='right')
        ax.set_ylabel('Scoring Rate (%)')
        ax.set_title('Scoring Rate by Starting Field Position')
        ax.set_ylim(0, 100)
    
    def _plot_zone_efficiency(self, ax, zones, avg_yards):
        """Plot efficiency by field zone"""
        colors = [PerformanceColors.get_performance_color(yards * 15) for yards in avg_yards]
        bars = ax.barh(zones, avg_yards, color=colors, alpha=0.85)
        
        for bar, yards in zip(bars, avg_yards):
            width = bar.get_width()
            ax.text(width + 0.1, bar.get_y() + bar.get_height()/2,
                   f'{yards:.1f}', ha='left', va='center',
                   **self.theme.font_manager.get_text_properties('data_labels',
                                                               self.theme.config.primary_text_color))
        
        ax.set_xlabel('Average Yards per Play')
        ax.set_title('Offensive Efficiency by Field Zone')
    
    def _plot_field_heatmap(self, ax, field_zones):
        """Create field position heat map visualization"""
        # Simplified field representation
        field_length = 100
        field_width = 20
        
        # Create field background
        field_rect = Rectangle((0, 0), field_length, field_width, 
                             facecolor=self.theme.config.background_color,
                             edgecolor='white', linewidth=2)
        ax.add_patch(field_rect)
        
        # Add yard lines
        for yard in range(0, 101, 10):
            ax.axvline(x=yard, color='white', alpha=0.3, linewidth=1)
        
        # Add zone coloring based on scoring rates
        zone_boundaries = [0, 20, 40, 50, 70, 80, 100]
        zone_data = list(field_zones.values())
        
        for i in range(len(zone_boundaries) - 1):
            start = zone_boundaries[i]
            end = zone_boundaries[i + 1]
            if i < len(zone_data):
                scoring_rate = zone_data[i]['scoring_rate']
                color = PerformanceColors.get_performance_color(scoring_rate)
                
                zone_rect = Rectangle((start, 2), end - start, field_width - 4,
                                    facecolor=color, alpha=0.4)
                ax.add_patch(zone_rect)
                
                # Add zone label
                ax.text(start + (end - start) / 2, field_width / 2,
                       f'{scoring_rate}%', ha='center', va='center',
                       **self.theme.font_manager.get_text_properties('data_labels',
                                                                   self.theme.config.primary_text_color))
        
        ax.set_xlim(0, 100)
        ax.set_ylim(0, field_width)
        ax.set_xlabel('Field Position (Yard Line)')
        ax.set_title('Field Position Scoring Heat Map')
        ax.set_aspect('equal')
        
        # Remove y-axis ticks
        ax.set_yticks([])
        
        # Add end zone labels
        ax.text(-5, field_width / 2, 'Own\nGoal', ha='center', va='center', rotation=90,
               **self.theme.font_manager.get_text_properties('annotations',
                                                           self.theme.config.secondary_text_color))
        ax.text(105, field_width / 2, 'Opp\nGoal', ha='center', va='center', rotation=90,
               **self.theme.font_manager.get_text_properties('annotations',
                                                           self.theme.config.secondary_text_color))