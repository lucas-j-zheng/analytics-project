"""
FootballViz Typography System

Professional font specifications optimized for coaching staff readability:
- Font hierarchy (title, axis labels, tick labels, annotations)
- Size specifications for different output formats
- Weight and style management
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm


@dataclass
class FontSpecification:
    """Font specification for different text elements"""
    
    family: str
    size: int
    weight: str
    style: str = 'normal'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to matplotlib font properties dictionary"""
        return {
            'family': self.family,
            'size': self.size,
            'weight': self.weight,
            'style': self.style
        }


class FontManager:
    """Professional font management for football analytics"""
    
    # Font family preferences (in order of preference)
    PRIMARY_FONTS = ['Arial', 'Helvetica', 'DejaVu Sans']
    MONOSPACE_FONTS = ['Courier New', 'DejaVu Sans Mono', 'monospace'] 
    
    def __init__(self, output_format: str = 'screen'):
        """
        Initialize font manager
        
        Args:
            output_format: 'screen', 'presentation', 'print', or 'web'
        """
        self.output_format = output_format
        self.base_size = self._get_base_size()
        self._setup_fonts()
    
    def _get_base_size(self) -> int:
        """Get base font size based on output format"""
        size_map = {
            'screen': 12,
            'presentation': 16,
            'print': 10,
            'web': 14
        }
        return size_map.get(self.output_format, 12)
    
    def _setup_fonts(self):
        """Set up font specifications for different text elements"""
        
        # Find available font family
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        self.font_family = next(
            (font for font in self.PRIMARY_FONTS if font in available_fonts),
            'sans-serif'
        )
        
        # Define font specifications based on hierarchy
        self.specifications = {
            'title': FontSpecification(
                family=self.font_family,
                size=int(self.base_size * 1.5),  # 150% of base
                weight='bold'
            ),
            'subtitle': FontSpecification(
                family=self.font_family,
                size=int(self.base_size * 1.25),  # 125% of base
                weight='bold'
            ),
            'axis_labels': FontSpecification(
                family=self.font_family,
                size=int(self.base_size * 1.1),   # 110% of base
                weight='medium'
            ),
            'tick_labels': FontSpecification(
                family=self.font_family,
                size=self.base_size,              # 100% of base
                weight='normal'
            ),
            'annotations': FontSpecification(
                family=self.font_family,
                size=int(self.base_size * 0.9),   # 90% of base
                weight='normal'
            ),
            'legend': FontSpecification(
                family=self.font_family,
                size=int(self.base_size * 0.95),  # 95% of base
                weight='normal'
            ),
            'data_labels': FontSpecification(
                family=self.font_family,
                size=int(self.base_size * 0.85),  # 85% of base
                weight='bold'
            ),
            'monospace': FontSpecification(
                family=next(
                    (font for font in self.MONOSPACE_FONTS if font in available_fonts),
                    'monospace'
                ),
                size=self.base_size,
                weight='normal'
            )
        }
    
    def get_font(self, element_type: str) -> Dict[str, Any]:
        """
        Get font properties for specific element type
        
        Args:
            element_type: Type of text element
            
        Returns:
            Font properties dictionary for matplotlib
        """
        if element_type not in self.specifications:
            element_type = 'tick_labels'  # Default fallback
        
        return self.specifications[element_type].to_dict()
    
    def apply_to_axes(self, ax, **kwargs):
        """
        Apply font specifications to matplotlib axes
        
        Args:
            ax: Matplotlib axes object
            **kwargs: Override specific font properties
        """
        # Title
        if ax.get_title():
            title_font = self.get_font('title')
            title_font.update(kwargs.get('title', {}))
            ax.set_title(ax.get_title(), **title_font)
        
        # Axis labels
        xlabel_font = self.get_font('axis_labels') 
        xlabel_font.update(kwargs.get('xlabel', {}))
        if ax.get_xlabel():
            ax.set_xlabel(ax.get_xlabel(), **xlabel_font)
        
        ylabel_font = self.get_font('axis_labels')
        ylabel_font.update(kwargs.get('ylabel', {}))
        if ax.get_ylabel():
            ax.set_ylabel(ax.get_ylabel(), **ylabel_font)
        
        # Tick labels
        tick_font = self.get_font('tick_labels')
        tick_font.update(kwargs.get('ticks', {}))
        ax.tick_params(labelsize=tick_font['size'])
        
        # Legend
        if ax.get_legend():
            legend_font = self.get_font('legend')
            legend_font.update(kwargs.get('legend', {}))
            ax.legend(prop=legend_font)
    
    def get_text_properties(self, element_type: str, color: str = '#FFFFFF') -> Dict[str, Any]:
        """
        Get complete text properties including color
        
        Args:
            element_type: Type of text element
            color: Text color
            
        Returns:
            Complete text properties dictionary
        """
        props = self.get_font(element_type)
        props['color'] = color
        return props
    
    @staticmethod
    def set_global_font_family(family: str):
        """
        Set global matplotlib font family
        
        Args:
            family: Font family name
        """
        plt.rcParams['font.family'] = family
    
    @staticmethod  
    def get_available_fonts() -> list:
        """Get list of available font families"""
        return sorted([f.name for f in fm.fontManager.ttflist])
    
    def scale_fonts(self, scale_factor: float):
        """
        Scale all font sizes by a factor
        
        Args:
            scale_factor: Scaling factor (1.0 = no change)
        """
        for spec in self.specifications.values():
            spec.size = int(spec.size * scale_factor)


# Pre-defined font configurations for different contexts
COACHING_STAFF_FONTS = FontManager('presentation')
WEB_INTERFACE_FONTS = FontManager('web') 
PRINT_REPORT_FONTS = FontManager('print')
SCREEN_DISPLAY_FONTS = FontManager('screen')

# Global font settings for matplotlib
def apply_global_font_settings(theme: str = 'professional'):
    """
    Apply global font settings to matplotlib
    
    Args:
        theme: Font theme ('professional', 'modern', 'classic')
    """
    if theme == 'professional':
        plt.rcParams.update({
            'font.family': 'Arial',
            'font.size': 12,
            'axes.titlesize': 18,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 11,
            'figure.titlesize': 20
        })
    elif theme == 'modern':
        plt.rcParams.update({
            'font.family': 'Helvetica',
            'font.size': 11,
            'axes.titlesize': 16,
            'axes.labelsize': 13,
            'xtick.labelsize': 11,
            'ytick.labelsize': 11,
            'legend.fontsize': 10,
            'figure.titlesize': 18
        })
    elif theme == 'classic':
        plt.rcParams.update({
            'font.family': 'serif',
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'xtick.labelsize': 12,
            'ytick.labelsize': 12,
            'legend.fontsize': 11,
            'figure.titlesize': 18
        })