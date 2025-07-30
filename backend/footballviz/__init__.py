"""
FootballViz - Professional Football Analytics Visualization Library

A specialized matplotlib wrapper designed for football analytics,
providing professional styling, preset templates, and football-specific
chart types optimized for coaching staff and team analysis.
"""

from .core.theme import FootballTheme, ThemeManager
from .charts.base import FootballChart
from .templates import (
    OffensiveEfficiency,
    DefensiveBreakdown,
    SituationalAnalysis,
    PerformanceComparison
)

__version__ = "1.0.0"
__author__ = "Football Analytics Platform"

# Default theme initialization
default_theme = FootballTheme()

# Available chart templates
CHART_TEMPLATES = {
    'offensive_efficiency': OffensiveEfficiency,
    'defensive_breakdown': DefensiveBreakdown, 
    'situational_analysis': SituationalAnalysis,
    'performance_comparison': PerformanceComparison
}

# Export main classes for easy import
__all__ = [
    'FootballTheme',
    'ThemeManager', 
    'FootballChart',
    'OffensiveEfficiency',
    'DefensiveBreakdown',
    'SituationalAnalysis', 
    'PerformanceComparison',
    'CHART_TEMPLATES'
]