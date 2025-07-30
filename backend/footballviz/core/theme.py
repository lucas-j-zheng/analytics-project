"""
FootballViz Theme Management System

Professional theming system that combines colors, fonts, and styling
for consistent, high-quality football analytics visualizations.
"""

from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from .colors import PerformanceColors, TeamColors, BackgroundThemes
from .fonts import FontManager


@dataclass
class ThemeConfiguration:
    """Complete theme configuration for FootballViz"""
    
    # Background and basic colors
    background_color: str = BackgroundThemes.CHARCOAL_PROFESSIONAL
    primary_text_color: str = '#FFFFFF'
    secondary_text_color: str = '#E5E5E7'
    tertiary_text_color: str = '#98989A'
    
    # Grid and axes
    grid_color: str = '#FFFFFF'
    grid_alpha: float = 0.15
    grid_style: str = '-'
    grid_width: float = 0.8
    
    # Axes styling
    spine_color: str = '#FFFFFF'
    spine_alpha: float = 0.4
    spine_width: float = 1.2
    show_top_spine: bool = False
    show_right_spine: bool = False
    
    # Team colors
    team_primary: str = TeamColors.PRIMARY
    team_secondary: str = TeamColors.SECONDARY
    opponent_color: str = TeamColors.OPPONENT
    
    # Chart styling
    bar_edge_color: str = '#FFFFFF'
    bar_edge_width: float = 0.8
    bar_alpha: float = 0.85
    line_width: float = 3.0
    marker_size: float = 8.0
    marker_edge_width: float = 1.5
    marker_edge_color: str = '#FFFFFF'
    
    # Layout
    figure_facecolor: str = field(init=False)
    axes_facecolor: str = field(init=False)
    title_pad: float = 25
    axis_label_pad: float = 15
    tight_layout_pad: float = 2.0
    
    # Export settings
    dpi_screen: int = 150
    dpi_presentation: int = 300
    dpi_print: int = 600
    
    def __post_init__(self):
        """Set derived colors after initialization"""
        self.figure_facecolor = self.background_color
        self.axes_facecolor = self.background_color


class FootballTheme:
    """Professional football analytics theme manager"""
    
    def __init__(self, 
                 theme_name: str = 'charcoal_professional',
                 team_primary: Optional[str] = None,
                 team_secondary: Optional[str] = None):
        """
        Initialize football theme
        
        Args:
            theme_name: Base theme name
            team_primary: Custom team primary color
            team_secondary: Custom team secondary color
        """
        self.theme_name = theme_name
        self.config = self._build_theme_config(theme_name, team_primary, team_secondary)
        self.font_manager = FontManager('screen')
        self.performance_colors = PerformanceColors()
        
    def _build_theme_config(self, 
                           theme_name: str,
                           team_primary: Optional[str] = None,
                           team_secondary: Optional[str] = None) -> ThemeConfiguration:
        """Build theme configuration from base theme"""
        
        # Get base theme colors
        base_colors = BackgroundThemes.get_theme_colors(
            theme_name.split('_')[0] if '_' in theme_name else theme_name
        )
        
        # Create configuration
        config = ThemeConfiguration(
            background_color=base_colors['background'],
            primary_text_color=base_colors['primary_text'],
            secondary_text_color=base_colors['secondary_text'],
            tertiary_text_color=base_colors['tertiary_text'],
            grid_color=base_colors['grid'],
            grid_alpha=base_colors['grid_alpha']
        )
        
        # Override team colors if provided
        if team_primary:
            config.team_primary = team_primary
        if team_secondary:
            config.team_secondary = team_secondary
            
        return config
    
    def apply_to_figure(self, fig, ax=None):
        """
        Apply theme to matplotlib figure and axes
        
        Args:
            fig: Matplotlib figure
            ax: Matplotlib axes (if None, applies to all axes)
        """
        # Figure styling
        fig.patch.set_facecolor(self.config.figure_facecolor)
        
        # Apply to all axes if none specified
        axes_list = [ax] if ax else fig.get_axes()
        
        for axis in axes_list:
            self._apply_to_axes(axis)
    
    def _apply_to_axes(self, ax):
        """Apply theme styling to specific axes"""
        
        # Axes background
        ax.set_facecolor(self.config.axes_facecolor)
        
        # Grid styling
        ax.grid(True, 
                color=self.config.grid_color,
                alpha=self.config.grid_alpha,
                linestyle=self.config.grid_style,
                linewidth=self.config.grid_width)
        ax.set_axisbelow(True)  # Grid behind data
        
        # Spine styling
        for spine_name, spine in ax.spines.items():
            if spine_name in ['top', 'right'] and not getattr(self.config, f'show_{spine_name}_spine'):
                spine.set_visible(False)
            else:
                spine.set_color(self.config.spine_color)
                spine.set_alpha(self.config.spine_alpha)
                spine.set_linewidth(self.config.spine_width)
        
        # Tick styling
        ax.tick_params(colors=self.config.primary_text_color,
                      which='both',
                      direction='out',
                      length=4,
                      width=1)
        
        # Apply fonts
        self.font_manager.apply_to_axes(ax, 
                                       title={'color': self.config.primary_text_color},
                                       xlabel={'color': self.config.secondary_text_color},
                                       ylabel={'color': self.config.secondary_text_color})
    
    def get_color_palette(self, palette_type: str = 'performance', n_colors: int = 5) -> list:
        """
        Get color palette for specific chart type
        
        Args:
            palette_type: Type of palette ('performance', 'team', 'comparison')
            n_colors: Number of colors needed
            
        Returns:
            List of hex color strings
        """
        if palette_type == 'performance':
            return self.performance_colors.get_gradient_colors(n_colors)
        elif palette_type == 'team':
            return [
                self.config.team_primary,
                self.config.team_secondary,
                self.config.opponent_color,
                self.performance_colors.NEUTRAL
            ][:n_colors]
        elif palette_type == 'comparison':
            return [
                self.config.team_primary,
                self.config.opponent_color,
                self.performance_colors.NEUTRAL,
                self.performance_colors.EMPHASIS
            ][:n_colors]
        else:
            return self.performance_colors.get_gradient_colors(n_colors)
    
    def style_bar_chart(self, ax, bars, style_type: str = 'default'):
        """
        Apply theme-specific styling to bar chart
        
        Args:
            ax: Matplotlib axes
            bars: Bar container from ax.bar()
            style_type: Styling variant ('default', 'performance', 'comparison')
        """
        for bar in bars:
            bar.set_edgecolor(self.config.bar_edge_color)
            bar.set_linewidth(self.config.bar_edge_width)
            bar.set_alpha(self.config.bar_alpha)
            
            # Add subtle gradient effect
            if style_type == 'performance':
                self._add_gradient_to_bar(bar)
    
    def style_line_chart(self, ax, lines, style_type: str = 'default'):
        """
        Apply theme-specific styling to line chart
        
        Args:
            ax: Matplotlib axes
            lines: Line objects from ax.plot()
            style_type: Styling variant ('default', 'trend', 'comparison')
        """
        for line in lines:
            line.set_linewidth(self.config.line_width)
            line.set_markeredgecolor(self.config.marker_edge_color)
            line.set_markeredgewidth(self.config.marker_edge_width)
            line.set_markersize(self.config.marker_size)
            
            if style_type == 'trend':
                line.set_linestyle('--')
                line.set_alpha(0.7)
    
    def _add_gradient_to_bar(self, bar):
        """Add subtle gradient effect to bar"""
        # This would require more complex matplotlib operations
        # For now, we'll keep the simple styling
        pass
    
    def create_legend(self, ax, labels: list, colors: list = None, 
                     location: str = 'upper right') -> patches.Rectangle:
        """
        Create themed legend
        
        Args:
            ax: Matplotlib axes
            labels: Legend labels
            colors: Legend colors (optional)
            location: Legend location
            
        Returns:
            Legend object
        """
        if colors is None:
            colors = self.get_color_palette('performance', len(labels))
        
        legend = ax.legend(labels,
                          loc=location,
                          frameon=False,
                          prop=self.font_manager.get_font('legend'))
        
        # Style legend text
        for text in legend.get_texts():
            text.set_color(self.config.secondary_text_color)
        
        return legend
    
    def add_performance_zones(self, ax, y_data: list, zones: Dict[str, Tuple[float, float]]):
        """
        Add performance zone backgrounds
        
        Args:
            ax: Matplotlib axes
            y_data: Y-axis data for determining zones
            zones: Dictionary mapping zone names to (min, max) tuples
        """
        y_min, y_max = min(y_data), max(y_data)
        
        zone_colors = {
            'elite': self.performance_colors.ELITE,
            'good': self.performance_colors.GOOD,
            'average': self.performance_colors.AVERAGE,
            'below_average': self.performance_colors.BELOW_AVERAGE,
            'concern': self.performance_colors.CONCERN
        }
        
        for zone_name, (zone_min, zone_max) in zones.items():
            if zone_name in zone_colors:
                ax.axhspan(zone_min, zone_max,
                          color=zone_colors[zone_name],
                          alpha=0.1,
                          zorder=0)
    
    def export_config(self) -> Dict[str, Any]:
        """Export theme configuration as dictionary"""
        return {
            'theme_name': self.theme_name,
            'config': self.config.__dict__,
            'font_settings': {
                'base_size': self.font_manager.base_size,
                'font_family': self.font_manager.font_family
            }
        }
    
    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]) -> 'FootballTheme':
        """Create theme from configuration dictionary"""
        theme = cls(config_dict['theme_name'])
        
        # Update configuration
        for key, value in config_dict['config'].items():
            if hasattr(theme.config, key):
                setattr(theme.config, key, value)
        
        return theme


class ThemeManager:
    """Manage multiple themes and provide theme switching capabilities"""
    
    PREDEFINED_THEMES = {
        'charcoal_professional': 'Professional dark theme with charcoal background',
        'field_turf': 'Football field inspired green theme',
        'chalkboard': 'Tactical chalkboard theme',
        'press_box': 'Stadium night lighting theme',
        'clean_presentation': 'Light theme for presentations'
    }
    
    def __init__(self):
        self.current_theme = None
        self.theme_cache = {}
    
    def get_theme(self, theme_name: str, **kwargs) -> FootballTheme:
        """
        Get or create theme instance
        
        Args:
            theme_name: Theme identifier
            **kwargs: Theme customization options
            
        Returns:
            FootballTheme instance
        """
        cache_key = f"{theme_name}_{hash(str(sorted(kwargs.items())))}"
        
        if cache_key not in self.theme_cache:
            self.theme_cache[cache_key] = FootballTheme(theme_name, **kwargs)
        
        return self.theme_cache[cache_key]
    
    def set_current_theme(self, theme_name: str, **kwargs):
        """Set current active theme"""
        self.current_theme = self.get_theme(theme_name, **kwargs)
    
    def apply_current_theme(self, fig, ax=None):
        """Apply current theme to figure"""
        if self.current_theme:
            self.current_theme.apply_to_figure(fig, ax)
    
    def list_available_themes(self) -> Dict[str, str]:
        """List all available predefined themes"""
        return self.PREDEFINED_THEMES.copy()
    
    def create_custom_theme(self, name: str, base_theme: str = 'charcoal_professional', 
                           **customizations) -> FootballTheme:
        """
        Create custom theme based on existing theme
        
        Args:
            name: Custom theme name
            base_theme: Base theme to modify
            **customizations: Theme property overrides
            
        Returns:
            Custom FootballTheme instance
        """
        theme = self.get_theme(base_theme)
        
        # Apply customizations
        for key, value in customizations.items():
            if hasattr(theme.config, key):
                setattr(theme.config, key, value)
        
        # Cache custom theme
        self.theme_cache[name] = theme
        
        return theme


# Global theme manager instance
theme_manager = ThemeManager()

# Set default theme
theme_manager.set_current_theme('charcoal_professional')