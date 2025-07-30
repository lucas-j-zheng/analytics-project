"""
FootballViz Core Module

Contains the foundational components for professional football analytics visualization:
- Theme management and styling
- Color schemes and performance-based coding
- Typography specifications
- Base configuration classes
"""

from .theme import FootballTheme, ThemeManager
from .colors import PerformanceColors, TeamColors
from .fonts import FontManager

__all__ = ['FootballTheme', 'ThemeManager', 'PerformanceColors', 'TeamColors', 'FontManager']