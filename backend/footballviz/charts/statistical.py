"""
Statistical Analysis Charts - Seaborn-inspired visualizations for football data

This module provides statistical visualization capabilities similar to seaborn
but optimized for football analytics data.
"""

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for thread safety
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd
import io
import base64
from typing import List, Dict, Any, Optional, Tuple
from scipy import stats
import seaborn as sns
from .base import FootballChart
from ..core.theme import FootballTheme

# Configure matplotlib for thread safety
plt.ioff()  # Turn off interactive mode

class StatisticalChart(FootballChart):
    """Base class for statistical football charts"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set seaborn style for statistical plots
        plt.style.use('default')
        sns.set_palette("husl")
    
    def plot(self):
        """Implementation required by abstract base class"""
        pass
    
    def _save_chart(self, fig) -> str:
        """Save chart figure to base64 string"""
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        chart_data = buffer.getvalue()
        buffer.close()
        plt.close(fig)  # Close figure to free memory
        return base64.b64encode(chart_data).decode('utf-8')
    
    def _create_error_chart(self, error_message: str) -> str:
        """Create an error chart with message"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, f"Error: {error_message}", 
               horizontalalignment='center', verticalalignment='center',
               transform=ax.transAxes, fontsize=14, color='red')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return self._save_chart(fig)
    
    def _prepare_dataframe(self, plays_data: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert plays data to pandas DataFrame for statistical analysis"""
        df = pd.DataFrame(plays_data)
        
        # Add derived columns for analysis
        if 'yards_gained' in df.columns:
            df['success'] = (df['yards_gained'] >= 0).astype(int)
            df['big_play'] = (df['yards_gained'] >= 15).astype(int)
            df['negative_play'] = (df['yards_gained'] < 0).astype(int)
        
        # Add situational columns
        if 'down' in df.columns and 'distance' in df.columns:
            df['down_distance'] = df['down'].astype(str) + ' & ' + df['distance'].astype(str)
            df['short_yardage'] = (df['distance'] <= 3).astype(int)
            df['long_yardage'] = (df['distance'] >= 8).astype(int)
        
        # Add field position categories
        if 'yard_line' in df.columns:
            df['field_zone'] = pd.cut(df['yard_line'], 
                                    bins=[0, 20, 50, 80, 100],
                                    labels=['Own 20', 'Own 50', 'Opp 50', 'Red Zone'])
        
        return df

class DistributionChart(StatisticalChart):
    """Distribution plots for football metrics"""
    
    def create_yards_distribution(self, plays_data: List[Dict[str, Any]], 
                                group_by: Optional[str] = None) -> str:
        """Create distribution plot of yards gained"""
        df = self._prepare_dataframe(plays_data)
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Yards Gained Distribution Analysis', 
                    fontsize=16, fontweight='bold', y=0.95)
        
        # Histogram with KDE
        ax1 = axes[0, 0]
        sns.histplot(data=df, x='yards_gained', kde=True, ax=ax1)
        ax1.set_title('Overall Distribution')
        ax1.axvline(df['yards_gained'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["yards_gained"].mean():.1f}')
        ax1.legend()
        
        # Box plot by group
        if group_by and group_by in df.columns:
            ax2 = axes[0, 1]
            sns.boxplot(data=df, x=group_by, y='yards_gained', ax=ax2)
            ax2.set_title(f'Distribution by {group_by.replace("_", " ").title()}')
            ax2.tick_params(axis='x', rotation=45)
        
        # Violin plot
        ax3 = axes[1, 0]
        if group_by and group_by in df.columns:
            sns.violinplot(data=df, x=group_by, y='yards_gained', ax=ax3)
            ax3.set_title(f'Density by {group_by.replace("_", " ").title()}')
            ax3.tick_params(axis='x', rotation=45)
        else:
            sns.violinplot(data=df, y='yards_gained', ax=ax3)
            ax3.set_title('Density Distribution')
        
        # QQ plot for normality
        ax4 = axes[1, 1]
        stats.probplot(df['yards_gained'], dist="norm", plot=ax4)
        ax4.set_title('Q-Q Plot (Normality Check)')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        return self._save_chart(fig)
    
    def create_correlation_heatmap(self, plays_data: List[Dict[str, Any]]) -> str:
        """Create correlation heatmap of numeric variables"""
        df = self._prepare_dataframe(plays_data)
        
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlation_matrix = df[numeric_cols].corr()
        
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Create heatmap
        sns.heatmap(correlation_matrix, 
                   annot=True, 
                   cmap='RdBu_r', 
                   center=0,
                   square=True,
                   fmt='.2f',
                   cbar_kws={'shrink': 0.8},
                   ax=ax)
        
        ax.set_title('Variable Correlation Matrix', 
                    fontsize=16, fontweight='bold', pad=20)
        
        plt.tight_layout()
        return self._save_chart(fig)

class RegressionChart(StatisticalChart):
    """Regression and relationship analysis charts"""
    
    def create_scatter_with_regression(self, plays_data: List[Dict[str, Any]],
                                     x_col: str, y_col: str,
                                     hue_col: Optional[str] = None) -> str:
        """Create scatter plot with regression line"""
        df = self._prepare_dataframe(plays_data)
        
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Scatter with regression
        ax1 = axes[0]
        if hue_col and hue_col in df.columns:
            sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col, ax=ax1)
        else:
            sns.scatterplot(data=df, x=x_col, y=y_col, ax=ax1)
        
        # Add regression line
        sns.regplot(data=df, x=x_col, y=y_col, scatter=False, ax=ax1)
        
        # Calculate correlation
        correlation = df[x_col].corr(df[y_col])
        ax1.set_title(f'{y_col.replace("_", " ").title()} vs {x_col.replace("_", " ").title()}\n' +
                     f'Correlation: {correlation:.3f}')
        
        # Residual plot
        ax2 = axes[1]
        sns.residplot(data=df, x=x_col, y=y_col, ax=ax2)
        ax2.set_title('Residual Plot')
        ax2.axhline(y=0, color='red', linestyle='--')
        
        plt.tight_layout()
        return self._save_chart(fig)
    
    def create_performance_trends(self, plays_data: List[Dict[str, Any]]) -> str:
        """Create trend analysis over game progression"""
        df = self._prepare_dataframe(plays_data)
        
        if 'play_id' not in df.columns:
            return self._create_error_chart("Play ID not available for trend analysis")
        
        # Sort by play order
        df = df.sort_values('play_id')
        
        # Calculate rolling averages
        df['rolling_avg_yards'] = df['yards_gained'].rolling(window=5, min_periods=1).mean()
        df['cumulative_yards'] = df['yards_gained'].cumsum()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Performance Trends Throughout Game', fontsize=16, fontweight='bold')
        
        # Rolling average
        ax1 = axes[0, 0]
        ax1.plot(df['play_id'], df['rolling_avg_yards'], linewidth=2)
        ax1.set_title('5-Play Rolling Average (Yards)')
        ax1.set_xlabel('Play Number')
        ax1.set_ylabel('Average Yards')
        ax1.grid(True, alpha=0.3)
        
        # Cumulative yards
        ax2 = axes[0, 1]
        ax2.plot(df['play_id'], df['cumulative_yards'], linewidth=2, color='green')
        ax2.set_title('Cumulative Yards Gained')
        ax2.set_xlabel('Play Number')
        ax2.set_ylabel('Total Yards')
        ax2.grid(True, alpha=0.3)
        
        # Success rate by quarter
        if 'quarter' in df.columns:
            ax3 = axes[1, 0]
            quarter_success = df.groupby('quarter')['success'].mean()
            quarter_success.plot(kind='bar', ax=ax3, color='skyblue')
            ax3.set_title('Success Rate by Quarter')
            ax3.set_ylabel('Success Rate')
            ax3.tick_params(axis='x', rotation=0)
        
        # Play distribution
        ax4 = axes[1, 1]
        if 'play_type' in df.columns:
            play_counts = df['play_type'].value_counts()
            ax4.pie(play_counts.values, labels=play_counts.index, autopct='%1.1f%%')
            ax4.set_title('Play Type Distribution')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        return self._save_chart(fig)

class ComparisonChart(StatisticalChart):
    """Comparative analysis charts"""
    
    def create_formation_comparison(self, plays_data: List[Dict[str, Any]]) -> str:
        """Compare performance across formations"""
        df = self._prepare_dataframe(plays_data)
        
        if 'formation' not in df.columns:
            return self._create_error_chart("Formation data not available")
        
        # Calculate formation statistics
        formation_stats = df.groupby('formation').agg({
            'yards_gained': ['count', 'mean', 'std'],
            'success': 'mean',
            'big_play': 'mean'
        }).round(2)
        
        formation_stats.columns = ['plays', 'avg_yards', 'std_yards', 'success_rate', 'big_play_rate']
        formation_stats = formation_stats.reset_index()
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Formation Performance Analysis', fontsize=16, fontweight='bold')
        
        # Average yards by formation
        ax1 = axes[0, 0]
        sns.barplot(data=formation_stats, x='formation', y='avg_yards', ax=ax1)
        ax1.set_title('Average Yards by Formation')
        ax1.tick_params(axis='x', rotation=45)
        
        # Success rate comparison
        ax2 = axes[0, 1]
        sns.barplot(data=formation_stats, x='formation', y='success_rate', ax=ax2)
        ax2.set_title('Success Rate by Formation')
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_ylabel('Success Rate')
        
        # Yards distribution by formation
        ax3 = axes[1, 0]
        sns.boxplot(data=df, x='formation', y='yards_gained', ax=ax3)
        ax3.set_title('Yards Distribution by Formation')
        ax3.tick_params(axis='x', rotation=45)
        
        # Efficiency scatter
        ax4 = axes[1, 1]
        ax4.scatter(formation_stats['plays'], formation_stats['avg_yards'], 
                   s=formation_stats['success_rate']*500, alpha=0.7)
        
        for i, row in formation_stats.iterrows():
            ax4.annotate(row['formation'], 
                        (row['plays'], row['avg_yards']),
                        xytext=(5, 5), textcoords='offset points',
                        fontsize=9)
        
        ax4.set_xlabel('Number of Plays')
        ax4.set_ylabel('Average Yards')
        ax4.set_title('Formation Efficiency\n(Bubble size = Success Rate)')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        return self._save_chart(fig)
    
    def create_situational_analysis(self, plays_data: List[Dict[str, Any]]) -> str:
        """Analyze performance in different game situations"""
        df = self._prepare_dataframe(plays_data)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Situational Performance Analysis', fontsize=16, fontweight='bold')
        
        # Down and distance heatmap
        if 'down' in df.columns and 'distance' in df.columns:
            ax1 = axes[0, 0]
            pivot_table = df.pivot_table(values='yards_gained', 
                                       index='down', 
                                       columns='distance', 
                                       aggfunc='mean')
            sns.heatmap(pivot_table, annot=True, fmt='.1f', cmap='RdYlGn', ax=ax1)
            ax1.set_title('Average Yards by Down & Distance')
        
        # Field position analysis
        if 'field_zone' in df.columns:
            ax2 = axes[0, 1]
            zone_stats = df.groupby('field_zone')['yards_gained'].mean()
            zone_stats.plot(kind='bar', ax=ax2, color='lightblue')
            ax2.set_title('Performance by Field Zone')
            ax2.tick_params(axis='x', rotation=45)
            ax2.set_ylabel('Average Yards')
        
        # Third down efficiency
        ax3 = axes[1, 0]
        if 'down' in df.columns:
            third_down = df[df['down'] == 3]
            if len(third_down) > 0:
                success_by_distance = third_down.groupby('distance')['success'].mean()
                success_by_distance.plot(kind='line', marker='o', ax=ax3, linewidth=2)
                ax3.set_title('Third Down Success Rate by Distance')
                ax3.set_xlabel('Distance to Go')
                ax3.set_ylabel('Success Rate')
                ax3.grid(True, alpha=0.3)
        
        # Red zone performance
        ax4 = axes[1, 1]
        if 'yard_line' in df.columns:
            red_zone = df[df['yard_line'] >= 80]
            if len(red_zone) > 0:
                rz_performance = red_zone.groupby('play_type').agg({
                    'yards_gained': 'mean',
                    'points_scored': 'sum'
                })
                
                if not rz_performance.empty:
                    rz_performance['yards_gained'].plot(kind='bar', ax=ax4, color='red', alpha=0.7)
                    ax4.set_title('Red Zone Performance by Play Type')
                    ax4.tick_params(axis='x', rotation=45)
                    ax4.set_ylabel('Average Yards')
        
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        return self._save_chart(fig)

class FootballHeatmap(StatisticalChart):
    """Football field heatmaps and positional analysis"""
    
    def create_field_position_heatmap(self, plays_data: List[Dict[str, Any]]) -> str:
        """Create heatmap of play distribution across field"""
        df = self._prepare_dataframe(plays_data)
        
        if 'yard_line' not in df.columns:
            return self._create_error_chart("Yard line data not available")
        
        fig, ax = plt.subplots(figsize=(16, 8))
        
        # Create field representation
        field_length = 100
        field_width = 53
        
        # Draw field
        field = patches.Rectangle((0, 0), field_length, field_width, 
                                linewidth=2, edgecolor='white', 
                                facecolor='green', alpha=0.3)
        ax.add_patch(field)
        
        # Add yard lines
        for yard in range(10, 100, 10):
            ax.axvline(x=yard, color='white', linewidth=1, alpha=0.5)
            ax.text(yard, field_width + 2, str(yard), ha='center', fontsize=10)
        
        # Add goal lines
        ax.axvline(x=0, color='yellow', linewidth=3)
        ax.axvline(x=field_length, color='yellow', linewidth=3)
        
        # Plot play locations as heatmap
        if len(df) > 0:
            # Create bins for heatmap
            x_bins = np.linspace(0, 100, 21)  # 5-yard bins
            y_bins = np.linspace(0, field_width, 11)  # Field width bins
            
            # For simplicity, use yard_line for x and random y positions
            np.random.seed(42)  # For consistent results
            y_positions = np.random.uniform(0, field_width, len(df))
            
            # Create 2D histogram
            H, xedges, yedges = np.histogram2d(df['yard_line'], y_positions, 
                                             bins=[x_bins, y_bins])
            
            # Plot heatmap
            X, Y = np.meshgrid(xedges[:-1], yedges[:-1])
            im = ax.pcolormesh(X, Y, H.T, cmap='Reds', alpha=0.7)
            
            # Add colorbar
            cbar = plt.colorbar(im, ax=ax, shrink=0.8)
            cbar.set_label('Play Frequency', rotation=270, labelpad=20)
        
        ax.set_xlim(0, field_length)
        ax.set_ylim(0, field_width)
        ax.set_xlabel('Yard Line')
        ax.set_ylabel('Field Width (yards)')
        ax.set_aspect('equal')
        ax.set_title('Play Distribution Heatmap', fontsize=16, fontweight='bold', pad=20)
        
        # Add statistics
        stats_text = f"Total Plays: {len(df)}\n"
        if len(df) > 0:
            stats_text += f"Avg Yard Line: {df['yard_line'].mean():.1f}\n"
            stats_text += f"Red Zone Plays: {len(df[df['yard_line'] >= 80])}"
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
               verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return self._save_chart(fig)

# Chart factory function
def create_statistical_chart(chart_type: str, plays_data: List[Dict[str, Any]], 
                           **kwargs) -> str:
    """Factory function to create statistical charts"""
    
    if chart_type == 'distribution':
        chart = DistributionChart()
        return chart.create_yards_distribution(plays_data, kwargs.get('group_by'))
    
    elif chart_type == 'correlation':
        chart = DistributionChart()
        return chart.create_correlation_heatmap(plays_data)
    
    elif chart_type == 'regression':
        chart = RegressionChart()
        return chart.create_scatter_with_regression(
            plays_data, 
            kwargs.get('x_col', 'yard_line'), 
            kwargs.get('y_col', 'yards_gained'),
            kwargs.get('hue_col')
        )
    
    elif chart_type == 'trends':
        chart = RegressionChart()
        return chart.create_performance_trends(plays_data)
    
    elif chart_type == 'formation_comparison':
        chart = ComparisonChart()
        return chart.create_formation_comparison(plays_data)
    
    elif chart_type == 'situational':
        chart = ComparisonChart()
        return chart.create_situational_analysis(plays_data)
    
    elif chart_type == 'field_heatmap':
        chart = FootballHeatmap()
        return chart.create_field_position_heatmap(plays_data)
    
    else:
        # Create error chart
        chart = StatisticalChart()
        return chart._create_error_chart(f"Unknown chart type: {chart_type}")