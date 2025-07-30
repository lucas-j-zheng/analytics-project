"""
FootballViz Export Utilities

Export and formatting utilities for FootballViz charts:
- Multi-format export management
- Report generation integration
- Presentation optimization
"""

import io
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..charts.base import ChartExporter


class ExportManager:
    """
    Centralized export management for FootballViz charts
    """
    
    def __init__(self, output_dir: str = "exports"):
        """
        Initialize export manager
        
        Args:
            output_dir: Base directory for exports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def export_chart_collection(self, 
                               charts: List[Any],
                               base_filename: str,
                               formats: List[str] = ['png', 'pdf'],
                               preset: str = 'presentation') -> Dict[str, List[str]]:
        """
        Export multiple charts in specified formats
        
        Args:
            charts: List of FootballChart instances
            base_filename: Base filename for exports
            formats: List of export formats
            preset: Export preset to use
            
        Returns:
            Dictionary mapping formats to exported file paths
        """
        exported_files = {format_name: [] for format_name in formats}
        
        for i, chart in enumerate(charts):
            chart_filename = f"{base_filename}_chart_{i+1}"
            
            for format_name in formats:
                output_path = os.path.join(self.output_dir, f"{chart_filename}.{format_name}")
                ChartExporter.export_chart(chart, output_path, preset)
                exported_files[format_name].append(output_path)
        
        return exported_files
    
    def create_report_package(self, 
                            charts: List[Any],
                            metadata: Dict[str, Any],
                            package_name: str) -> str:
        """
        Create comprehensive report package with charts and metadata
        
        Args:
            charts: List of FootballChart instances
            metadata: Report metadata
            package_name: Name for the report package
            
        Returns:
            Path to created package
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        package_dir = os.path.join(self.output_dir, f"{package_name}_{timestamp}")
        os.makedirs(package_dir, exist_ok=True)
        
        # Export charts
        chart_files = self.export_chart_collection(
            charts, 
            os.path.join(package_dir, "chart"),
            formats=['png', 'pdf', 'svg']
        )
        
        # Create metadata file
        metadata_file = os.path.join(package_dir, "report_metadata.json")
        import json
        with open(metadata_file, 'w') as f:
            json.dump({
                **metadata,
                'generated_at': datetime.now().isoformat(),
                'chart_files': chart_files
            }, f, indent=2)
        
        return package_dir


class ReportGenerator:
    """
    Generate formatted reports combining multiple FootballViz charts
    """
    
    def __init__(self, theme_manager=None):
        """
        Initialize report generator
        
        Args:
            theme_manager: FootballViz theme manager instance
        """
        self.theme_manager = theme_manager
        self.export_manager = ExportManager()
    
    def generate_game_summary_report(self, 
                                   game_data: Dict[str, Any],
                                   charts: List[Any]) -> str:
        """
        Generate comprehensive game summary report
        
        Args:
            game_data: Game information and statistics
            charts: List of FootballChart instances
            
        Returns:
            Path to generated report
        """
        report_name = f"game_summary_{game_data.get('week', 'unknown')}_vs_{game_data.get('opponent', 'unknown').replace(' ', '_')}"
        
        metadata = {
            'report_type': 'game_summary',
            'game_info': game_data,
            'charts_included': len(charts),
            'theme': self.theme_manager.current_theme.theme_name if self.theme_manager else 'default'
        }
        
        return self.export_manager.create_report_package(charts, metadata, report_name)
    
    def generate_season_analysis_report(self,
                                      season_data: Dict[str, Any],
                                      charts: List[Any]) -> str:
        """
        Generate season analysis report
        
        Args:
            season_data: Season statistics and information
            charts: List of FootballChart instances
            
        Returns:
            Path to generated report
        """
        report_name = f"season_analysis_{season_data.get('year', 'unknown')}"
        
        metadata = {
            'report_type': 'season_analysis',
            'season_info': season_data,
            'charts_included': len(charts),
            'theme': self.theme_manager.current_theme.theme_name if self.theme_manager else 'default'
        }
        
        return self.export_manager.create_report_package(charts, metadata, report_name)
    
    def generate_comparison_report(self,
                                 comparison_data: Dict[str, Any],
                                 charts: List[Any]) -> str:
        """
        Generate team/game comparison report
        
        Args:
            comparison_data: Comparison analysis data
            charts: List of FootballChart instances
            
        Returns:
            Path to generated report
        """
        report_name = f"comparison_{comparison_data.get('comparison_type', 'unknown')}"
        
        metadata = {
            'report_type': 'comparison',
            'comparison_info': comparison_data,
            'charts_included': len(charts),
            'theme': self.theme_manager.current_theme.theme_name if self.theme_manager else 'default'
        }
        
        return self.export_manager.create_report_package(charts, metadata, report_name)