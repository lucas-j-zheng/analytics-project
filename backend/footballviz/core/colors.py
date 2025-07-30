"""
FootballViz Color System

Professional color schemes designed for football analytics:
- Performance-based color coding (elite to concern zones)
- Team color integration with automatic opponent detection
- High contrast themes suitable for coaching staff presentations
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import matplotlib.colors as mcolors


@dataclass
class PerformanceColors:
    """Performance-based color coding system for football analytics"""
    
    # Performance tier colors
    ELITE = '#00C896'          # Bright green (top 10%)
    GOOD = '#7ED321'           # Green (top 25%) 
    AVERAGE = '#F5A623'        # Gold/yellow (middle 50%)
    BELOW_AVERAGE = '#FF6B35'  # Orange (bottom 25%)
    CONCERN = '#D0021B'        # Red (bottom 10%)
    NEUTRAL = '#8E8E93'        # Gray for baseline/comparison
    
    # Accent colors
    EMPHASIS = '#FFD60A'       # Gold for highlights
    SUCCESS = '#34C759'        # Success indicator
    WARNING = '#FF9500'        # Warning indicator
    ERROR = '#FF3B30'          # Error indicator
    
    @classmethod
    def get_performance_color(cls, percentile: float) -> str:
        """
        Get color based on performance percentile
        
        Args:
            percentile: Performance percentile (0-100)
            
        Returns:
            Hex color string
        """
        if percentile >= 90:
            return cls.ELITE
        elif percentile >= 75:
            return cls.GOOD
        elif percentile >= 25:
            return cls.AVERAGE
        elif percentile >= 10:
            return cls.BELOW_AVERAGE
        else:
            return cls.CONCERN
    
    @classmethod
    def get_gradient_colors(cls, n_colors: int = 5) -> List[str]:
        """Generate gradient colors from concern to elite"""
        return [cls.CONCERN, cls.BELOW_AVERAGE, cls.AVERAGE, cls.GOOD, cls.ELITE][:n_colors]
    
    @classmethod
    def get_colormap(cls, name: str = 'football_performance') -> mcolors.LinearSegmentedColormap:
        """Create matplotlib colormap for performance visualization"""
        colors = cls.get_gradient_colors()
        return mcolors.LinearSegmentedColormap.from_list(name, colors)


@dataclass
class TeamColors:
    """Team color integration system"""
    
    # Default team colors (can be overridden)
    PRIMARY = '#1E3A8A'        # Default team primary (blue)
    SECONDARY = '#F59E0B'      # Default team secondary (gold)
    OPPONENT = '#DC2626'       # Default opponent color (red)
    
    def __init__(self, primary: Optional[str] = None, secondary: Optional[str] = None):
        if primary:
            self.PRIMARY = primary
        if secondary:
            self.SECONDARY = secondary
    
    @classmethod
    def get_contrast_color(cls, background_color: str) -> str:
        """
        Get high contrast text color for given background
        
        Args:
            background_color: Hex color string
            
        Returns:
            Either white or black for optimal contrast
        """
        # Convert hex to RGB
        hex_color = background_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Calculate luminance
        luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
        
        return '#FFFFFF' if luminance < 0.5 else '#000000'
    
    @classmethod
    def blend_colors(cls, color1: str, color2: str, ratio: float = 0.5) -> str:
        """
        Blend two hex colors
        
        Args:
            color1: First hex color
            color2: Second hex color  
            ratio: Blend ratio (0.0 = color1, 1.0 = color2)
            
        Returns:
            Blended hex color
        """
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(rgb):
            return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        blended = tuple(
            rgb1[i] * (1 - ratio) + rgb2[i] * ratio
            for i in range(3)
        )
        
        return rgb_to_hex(blended)


class BackgroundThemes:
    """Professional background themes for different contexts"""
    
    CHARCOAL_PROFESSIONAL = '#1C1C1E'  # Apple-inspired dark
    FIELD_TURF = '#0D2818'             # Deep forest green  
    CHALKBOARD = '#2D3E2F'             # Tactical board green
    PRESS_BOX = '#1A1D23'              # Stadium night lighting
    
    # Light themes for print/presentation
    CLEAN_WHITE = '#FFFFFF'            # Pure white
    LIGHT_GRAY = '#F8F9FA'             # Light gray background
    
    @classmethod
    def get_theme_colors(cls, theme_name: str) -> Dict[str, str]:
        """
        Get complete color scheme for a theme
        
        Args:
            theme_name: Theme identifier
            
        Returns:
            Dictionary with background, text, and accent colors
        """
        themes = {
            'charcoal': {
                'background': cls.CHARCOAL_PROFESSIONAL,
                'primary_text': '#FFFFFF',
                'secondary_text': '#E5E5E7', 
                'tertiary_text': '#98989A',
                'grid': '#FFFFFF',
                'grid_alpha': 0.15
            },
            'field': {
                'background': cls.FIELD_TURF,
                'primary_text': '#FFFFFF',
                'secondary_text': '#E5E5E7',
                'tertiary_text': '#98989A', 
                'grid': '#FFFFFF',
                'grid_alpha': 0.15
            },
            'chalkboard': {
                'background': cls.CHALKBOARD,
                'primary_text': '#FFFFFF',
                'secondary_text': '#E5E5E7',
                'tertiary_text': '#98989A',
                'grid': '#FFFFFF', 
                'grid_alpha': 0.15
            },
            'light': {
                'background': cls.CLEAN_WHITE,
                'primary_text': '#1F2937',
                'secondary_text': '#4B5563',
                'tertiary_text': '#6B7280',
                'grid': '#E5E7EB',
                'grid_alpha': 0.8
            }
        }
        
        return themes.get(theme_name, themes['charcoal'])


# Pre-defined color palettes for different chart types
OFFENSIVE_PALETTE = [
    PerformanceColors.GOOD,    # Successful plays
    PerformanceColors.AVERAGE, # Average plays  
    PerformanceColors.CONCERN, # Unsuccessful plays
    PerformanceColors.EMPHASIS # Highlight color
]

DEFENSIVE_PALETTE = [
    PerformanceColors.ELITE,   # Excellent defense
    PerformanceColors.GOOD,    # Good defense
    PerformanceColors.AVERAGE, # Average defense
    PerformanceColors.BELOW_AVERAGE, # Poor defense
    PerformanceColors.CONCERN  # Very poor defense
]

COMPARISON_PALETTE = [
    TeamColors.PRIMARY,        # Team performance
    TeamColors.OPPONENT,       # Opponent performance
    PerformanceColors.NEUTRAL, # League average
    PerformanceColors.EMPHASIS # Highlight/target
]