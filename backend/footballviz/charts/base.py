"""
FootballViz Base Chart Classes

Foundation classes for all football analytics visualizations with:
- Professional styling integration
- Export optimization
- Interactive parameter management
- Performance zone visualization
"""

import io
import base64
from typing import Dict, List, Any, Optional, Tuple, Union
from abc import ABC, abstractmethod
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from datetime import datetime

from ..core.theme import FootballTheme, theme_manager
from ..core.colors import PerformanceColors


class FootballChart(ABC):
    """
    Base class for all FootballViz charts
    
    Provides:
    - Professional theme integration
    - Consistent styling and layout
    - Export capabilities
    - Performance zone management
    """
    
    def __init__(self, 
                 width: float = 12, 
                 height: float = 8,
                 theme: Optional[FootballTheme] = None,
                 title: str = "",
                 subtitle: str = ""):
        """
        Initialize football chart
        
        Args:
            width: Figure width in inches
            height: Figure height in inches
            theme: FootballTheme instance (uses default if None)
            title: Chart title
            subtitle: Chart subtitle
        """
        self.width = width
        self.height = height
        self.theme = theme or theme_manager.current_theme or FootballTheme()
        self.title = title
        self.subtitle = subtitle
        
        # Chart components
        self.fig = None
        self.ax = None
        self.data = None
        self.chart_elements = {}
        
        # Styling options
        self.show_performance_zones = False
        self.performance_zones = {}
        self.annotations = []
        
        # Export settings
        self.export_settings = {
            'dpi': self.theme.config.dpi_screen,
            'bbox_inches': 'tight',
            'facecolor': self.theme.config.background_color,
            'edgecolor': 'none'
        }
    
    def create_figure(self) -> Tuple[plt.Figure, plt.Axes]:
        """
        Create and configure matplotlib figure and axes
        
        Returns:
            Tuple of (figure, axes)
        """
        self.fig, self.ax = plt.subplots(figsize=(self.width, self.height))
        
        # Apply theme
        self.theme.apply_to_figure(self.fig, self.ax)
        
        # Set titles
        if self.title:
            self.ax.set_title(self.title, 
                            pad=self.theme.config.title_pad,
                            **self.theme.font_manager.get_text_properties('title', 
                                                                        self.theme.config.primary_text_color))
        
        if self.subtitle:
            self.fig.suptitle(self.subtitle,
                            y=0.95,
                            **self.theme.font_manager.get_text_properties('subtitle',
                                                                        self.theme.config.secondary_text_color))
        
        return self.fig, self.ax
    
    @abstractmethod
    def plot(self, data: Dict[str, Any], **kwargs) -> 'FootballChart':
        """
        Create the chart visualization
        
        Args:
            data: Chart data dictionary
            **kwargs: Additional plotting parameters
            
        Returns:
            Self for method chaining
        """
        pass
    
    def add_performance_zones(self, zones: Dict[str, Tuple[float, float]]):
        """
        Add performance zone backgrounds
        
        Args:
            zones: Dictionary mapping zone names to (min, max) value tuples
        """
        self.show_performance_zones = True
        self.performance_zones = zones
        
        if self.ax:
            self.theme.add_performance_zones(self.ax, 
                                           list(self.data.values()) if self.data else [0, 100],
                                           zones)
    
    def add_annotation(self, 
                      x: float, 
                      y: float, 
                      text: str,
                      style: str = 'default',
                      color: Optional[str] = None):
        """
        Add annotation to chart
        
        Args:
            x: X coordinate
            y: Y coordinate  
            text: Annotation text
            style: Annotation style ('default', 'callout', 'highlight')
            color: Text color (uses theme default if None)
        """
        color = color or self.theme.config.tertiary_text_color
        
        annotation_props = self.theme.font_manager.get_text_properties('annotations', color)
        
        if style == 'callout':
            # Callout box with arrow
            bbox_props = dict(boxstyle="round,pad=0.3", 
                            facecolor=self.theme.config.background_color,
                            edgecolor=color,
                            alpha=0.8)
            arrowprops = dict(arrowstyle='->', color=color)
            
            annotation = self.ax.annotate(text, xy=(x, y), xytext=(10, 10),
                                        textcoords='offset points',
                                        bbox=bbox_props, 
                                        arrowprops=arrowprops,
                                        **annotation_props)
        elif style == 'highlight':
            # Highlighted background
            bbox_props = dict(boxstyle="round,pad=0.3",
                            facecolor=PerformanceColors.EMPHASIS,
                            alpha=0.3)
            annotation = self.ax.annotate(text, xy=(x, y), 
                                        bbox=bbox_props,
                                        **annotation_props)
        else:
            # Simple text annotation
            annotation = self.ax.annotate(text, xy=(x, y), **annotation_props)
        
        self.annotations.append({
            'annotation': annotation,
            'x': x, 'y': y, 
            'text': text, 
            'style': style
        })
    
    def add_reference_line(self, 
                          value: float, 
                          orientation: str = 'horizontal',
                          label: str = "",
                          color: Optional[str] = None,
                          style: str = '--'):
        """
        Add reference line (e.g., league average, target)
        
        Args:
            value: Line value
            orientation: 'horizontal' or 'vertical'
            label: Line label
            color: Line color
            style: Line style
        """
        color = color or PerformanceColors.NEUTRAL
        
        if orientation == 'horizontal':
            line = self.ax.axhline(y=value, color=color, linestyle=style, alpha=0.7, linewidth=2)
            if label:
                self.ax.text(0.02, value, label, 
                           transform=self.ax.get_yaxis_transform(),
                           **self.theme.font_manager.get_text_properties('annotations', color))
        else:
            line = self.ax.axvline(x=value, color=color, linestyle=style, alpha=0.7, linewidth=2)
            if label:
                self.ax.text(value, 0.98, label,
                           transform=self.ax.get_xaxis_transform(),
                           rotation=90,
                           **self.theme.font_manager.get_text_properties('annotations', color))
        
        return line
    
    def set_labels(self, xlabel: str = "", ylabel: str = "", **kwargs):
        """
        Set axis labels with proper styling
        
        Args:
            xlabel: X-axis label
            ylabel: Y-axis label
            **kwargs: Additional label properties
        """
        if xlabel:
            self.ax.set_xlabel(xlabel, 
                             labelpad=self.theme.config.axis_label_pad,
                             **self.theme.font_manager.get_text_properties('axis_labels',
                                                                         self.theme.config.secondary_text_color))
        
        if ylabel:
            self.ax.set_ylabel(ylabel,
                             labelpad=self.theme.config.axis_label_pad,
                             **self.theme.font_manager.get_text_properties('axis_labels',
                                                                         self.theme.config.secondary_text_color))
    
    def format_percentage_axis(self, ax_obj=None, axis: str = 'y'):
        """
        Format axis to show percentages
        
        Args:
            ax_obj: Matplotlib axes object (uses self.ax if None)
            axis: 'x' or 'y' axis to format
        """
        ax_obj = ax_obj or self.ax
        if axis == 'y':
            ax_obj.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))
        else:
            ax_obj.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))
    
    def add_data_labels(self, values: List[float], positions: List[Tuple[float, float]], 
                       format_func: Optional[callable] = None):
        """
        Add data labels to chart elements
        
        Args:
            values: Data values to display
            positions: Label positions as (x, y) tuples
            format_func: Function to format values (default: no formatting)
        """
        format_func = format_func or (lambda x: str(x))
        
        for value, (x, y) in zip(values, positions):
            formatted_value = format_func(value)
            self.ax.text(x, y, formatted_value,
                        ha='center', va='bottom',
                        **self.theme.font_manager.get_text_properties('data_labels',
                                                                     self.theme.config.primary_text_color))
    
    def optimize_layout(self):
        """Optimize chart layout for better presentation"""
        if self.fig:
            self.fig.tight_layout(pad=self.theme.config.tight_layout_pad)
    
    def to_base64(self, format: str = 'png', **kwargs) -> str:
        """
        Export chart as base64 encoded string
        
        Args:
            format: Image format ('png', 'jpg', 'svg')
            **kwargs: Additional export parameters
            
        Returns:
            Base64 encoded image string
        """
        if not self.fig:
            raise ValueError("No figure to export. Call plot() first.")
        
        buffer = io.BytesIO()
        export_settings = {**self.export_settings, **kwargs}
        
        self.fig.savefig(buffer, format=format, **export_settings)
        buffer.seek(0)
        
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        
        return f"data:image/{format.lower()};base64,{image_base64}"
    
    def save(self, filename: str, **kwargs):
        """
        Save chart to file
        
        Args:
            filename: Output filename
            **kwargs: Additional save parameters
        """
        if not self.fig:
            raise ValueError("No figure to save. Call plot() first.")
        
        export_settings = {**self.export_settings, **kwargs}
        self.fig.savefig(filename, **export_settings)
    
    def show(self):
        """Display chart"""
        if self.fig:
            plt.show()
    
    def close(self):
        """Close figure and free memory"""
        if self.fig:
            plt.close(self.fig)
            self.fig = None
            self.ax = None


class ChartExporter:
    """
    Utility class for optimized chart exports in different formats
    """
    
    EXPORT_PRESETS = {
        'presentation': {
            'dpi': 300,
            'figsize_multiplier': 1.0,
            'font_scale': 1.2,
            'description': 'High-res for projectors and presentations'
        },
        'print': {
            'dpi': 600,
            'figsize_multiplier': 0.8,
            'font_scale': 0.9,
            'description': 'Publication quality for reports'
        },
        'web': {
            'dpi': 150,
            'figsize_multiplier': 1.0,
            'font_scale': 1.0,
            'description': 'Optimized for web display'
        },
        'social': {
            'dpi': 200,
            'figsize_multiplier': 1.0,
            'font_scale': 1.1,
            'description': 'Social media optimized'
        }
    }
    
    @classmethod
    def export_chart(cls, 
                    chart: FootballChart,
                    filename: str,
                    preset: str = 'web',
                    custom_settings: Optional[Dict] = None) -> str:
        """
        Export chart with optimized settings
        
        Args:
            chart: FootballChart instance
            filename: Output filename
            preset: Export preset name
            custom_settings: Override settings
            
        Returns:
            Path to exported file
        """
        if preset not in cls.EXPORT_PRESETS:
            preset = 'web'
        
        settings = cls.EXPORT_PRESETS[preset].copy()
        if custom_settings:
            settings.update(custom_settings)
        
        # Apply font scaling
        if 'font_scale' in settings and settings['font_scale'] != 1.0:
            chart.theme.font_manager.scale_fonts(settings['font_scale'])
        
        # Apply DPI setting
        export_kwargs = {
            'dpi': settings['dpi'],
            'bbox_inches': 'tight',
            'facecolor': chart.theme.config.background_color,
            'edgecolor': 'none'
        }
        
        chart.save(filename, **export_kwargs)
        
        # Reset font scaling
        if 'font_scale' in settings and settings['font_scale'] != 1.0:
            chart.theme.font_manager.scale_fonts(1.0 / settings['font_scale'])
        
        return filename
    
    @classmethod
    def get_preset_info(cls) -> Dict[str, str]:
        """Get information about available export presets"""
        return {name: info['description'] for name, info in cls.EXPORT_PRESETS.items()}
    
    @classmethod
    def export_multiple_formats(cls,
                               chart: FootballChart,
                               base_filename: str,
                               formats: List[str] = ['png', 'pdf', 'svg']) -> List[str]:
        """
        Export chart in multiple formats
        
        Args:
            chart: FootballChart instance
            base_filename: Base filename (without extension)
            formats: List of formats to export
            
        Returns:
            List of exported filenames
        """
        exported_files = []
        
        for format_name in formats:
            filename = f"{base_filename}.{format_name}"
            chart.save(filename, format=format_name)
            exported_files.append(filename)
        
        return exported_files