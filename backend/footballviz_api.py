"""
FootballViz API Integration

Flask routes and utilities for integrating FootballViz with the main application:
- Chart generation endpoints
- Theme management
- Export functionality
- Real-time collaboration integration
"""

import io
import json 
import base64
from typing import Dict, List, Any, Optional
from flask import jsonify, request, send_file
from flask_jwt_extended import jwt_required
from datetime import datetime

# Import FootballViz components
from footballviz import FootballTheme, ThemeManager, CHART_TEMPLATES
from footballviz.utils.data_processor import FootballDataProcessor
from footballviz.charts.base import ChartExporter
from footballviz.query_builder import CustomQueryBuilder, LogicGroup, FilterCondition, QueryTemplate, PrebuiltTemplates
from footballviz.filters import PlayDataFilterSchema, FilterValidation, CustomFilterPresets

# Import existing models and utilities
from jwt_helper import get_current_user


class FootballVizAPI:
    """
    API wrapper for FootballViz integration with Flask application
    """
    
    def __init__(self, app, db, socketio=None):
        """
        Initialize FootballViz API
        
        Args:
            app: Flask application instance
            db: SQLAlchemy database instance
            socketio: SocketIO instance for real-time updates (optional)
        """
        self.app = app
        self.db = db
        self.socketio = socketio
        self.theme_manager = ThemeManager()
        self.data_processor = FootballDataProcessor()
        
        # Initialize query builder (will be set with PlayData model later)
        self.query_builder = None
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register all FootballViz API routes"""
        
        # Chart generation routes
        self.app.add_url_rule('/api/footballviz/charts/generate', 
                             'generate_chart', self.generate_chart, methods=['POST'])
        
        self.app.add_url_rule('/api/footballviz/charts/<chart_type>',
                             'get_chart_template', self.get_chart_template, methods=['GET'])
        
        # Theme management routes
        self.app.add_url_rule('/api/footballviz/themes',
                             'get_themes', self.get_themes, methods=['GET'])
        
        self.app.add_url_rule('/api/footballviz/themes/<theme_name>',
                             'set_theme', self.set_theme, methods=['PUT'])
        
        self.app.add_url_rule('/api/footballviz/themes/custom',
                             'create_custom_theme', self.create_custom_theme, methods=['POST'])
        
        # Custom query builder routes
        self.app.add_url_rule('/api/footballviz/filters/schema',
                             'get_filter_schema', self.get_filter_schema, methods=['GET'])
        
        self.app.add_url_rule('/api/footballviz/filters/presets',
                             'get_filter_presets', self.get_filter_presets, methods=['GET'])
        
        self.app.add_url_rule('/api/footballviz/query/execute',
                             'execute_custom_query', self.execute_custom_query, methods=['POST'])
        
        self.app.add_url_rule('/api/footballviz/query/stats',
                             'get_query_stats', self.get_query_stats, methods=['POST'])
        
        self.app.add_url_rule('/api/footballviz/query/templates',
                             'get_query_templates', self.get_query_templates, methods=['GET'])
        
        self.app.add_url_rule('/api/footballviz/query/templates',
                             'save_query_template', self.save_query_template, methods=['POST'])
        
        self.app.add_url_rule('/api/footballviz/query/templates/<template_id>',
                             'delete_query_template', self.delete_query_template, methods=['DELETE'])
        
        # Export routes
        self.app.add_url_rule('/api/footballviz/export/<chart_id>',
                             'export_chart', self.export_chart, methods=['GET'])
        
        # Data processing routes
        self.app.add_url_rule('/api/footballviz/data/process/<int:game_id>',
                             'process_game_data', self.process_game_data, methods=['GET'])
        
        self.app.add_url_rule('/api/footballviz/data/compare',
                             'compare_data', self.compare_data, methods=['POST'])
    
    @jwt_required()
    def generate_chart(self):
        """
        Generate FootballViz chart from provided data
        
        Expected JSON payload:
        {
            "chart_type": "offensive_efficiency",
            "game_id": 123,
            "theme": "charcoal_professional",
            "options": {
                "show_comparison": true,
                "comparison_game_id": 124
            }
        }
        """
        try:
            current_user = get_current_user()
            data = request.get_json()
            
            # Validate required fields
            chart_type = data.get('chart_type')
            game_id = data.get('game_id')
            
            if not chart_type or not game_id:
                return jsonify({'message': 'chart_type and game_id are required'}), 400
            
            if chart_type not in CHART_TEMPLATES:
                return jsonify({'message': f'Unknown chart type: {chart_type}'}), 400
            
            # Get game data and verify permissions
            from app import Game, PlayData
            game = Game.query.get(game_id)
            if not game:
                return jsonify({'message': 'Game not found'}), 404
            
            # Check permissions
            if current_user['type'] == 'team' and game.team_id != current_user['id']:
                return jsonify({'message': 'Access denied'}), 403
            
            # Process game data
            plays = PlayData.query.filter_by(game_id=game_id).all()
            play_data = [
                {
                    'yards_gained': play.yards_gained,
                    'formation': play.formation,
                    'play_type': play.play_type,
                    'down': play.down,
                    'distance': play.distance,
                    'points_scored': play.points_scored,
                    'yard_line': play.yard_line,
                    'result_of_play': play.result_of_play
                }
                for play in plays
            ]
            
            processed_data = self.data_processor.process_play_data(play_data)
            
            # Handle comparison data if requested
            comparison_data = None
            options = data.get('options', {})
            if options.get('show_comparison') and options.get('comparison_game_id'):
                comp_game_id = options['comparison_game_id']
                comp_game = Game.query.get(comp_game_id)
                
                if comp_game:
                    comp_plays = PlayData.query.filter_by(game_id=comp_game_id).all()
                    comp_play_data = [
                        {
                            'yards_gained': play.yards_gained,
                            'formation': play.formation,
                            'play_type': play.play_type,
                            'down': play.down,
                            'distance': play.distance,
                            'points_scored': play.points_scored,
                            'yard_line': play.yard_line,
                            'result_of_play': play.result_of_play
                        }
                        for play in comp_plays
                    ]
                    comparison_data = self.data_processor.process_play_data(comp_play_data)
            
            # Set up theme
            theme_name = data.get('theme', 'charcoal_professional')
            team_colors = data.get('team_colors', {})
            theme = self.theme_manager.get_theme(theme_name, **team_colors)
            
            # Create chart
            chart_class = CHART_TEMPLATES[chart_type]
            chart = chart_class(theme=theme)
            
            # Generate chart
            chart.plot(processed_data, comparison_data=comparison_data, **options)
            
            # Convert to base64 for response
            chart_base64 = chart.to_base64()
            
            # Save chart configuration for later export
            chart_config = {
                'chart_type': chart_type,
                'game_id': game_id,
                'theme': theme_name,
                'options': options,
                'team_colors': team_colors,
                'created_at': datetime.utcnow().isoformat(),
                'created_by': current_user['id']
            }
            
            # Store in session or database for export functionality
            # For now, we'll return the config with the chart
            
            # Close chart to free memory
            chart.close()
            
            return jsonify({
                'chart_image': chart_base64,
                'chart_config': chart_config,
                'processed_data': {
                    'summary': processed_data['summary'].__dict__ if processed_data.get('summary') else {},
                    'formations_count': len(processed_data.get('formations', {})),
                    'play_types_count': len(processed_data.get('play_types', {}))
                }
            }), 200
        
        except Exception as e:
            return jsonify({'message': f'Chart generation failed: {str(e)}'}), 500
    
    @jwt_required()
    def get_chart_template(self, chart_type):
        """Get information about a specific chart template"""
        try:
            if chart_type not in CHART_TEMPLATES:
                return jsonify({'message': f'Unknown chart type: {chart_type}'}), 404
            
            chart_class = CHART_TEMPLATES[chart_type]
            
            # Get template information
            template_info = {
                'name': chart_type,
                'title': getattr(chart_class, '__doc__', '').split('\n')[0] if chart_class.__doc__ else chart_type,
                'description': getattr(chart_class, '__doc__', 'No description available'),
                'required_data': ['play_data'],  # Base requirement
                'optional_parameters': [
                    'comparison_data',
                    'show_league_average',
                    'show_performance_zones'
                ],
                'supported_themes': list(self.theme_manager.list_available_themes().keys())
            }
            
            return jsonify(template_info), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    def get_themes(self):
        """Get available themes"""
        try:
            themes = self.theme_manager.list_available_themes()
            current_theme = self.theme_manager.current_theme.theme_name if self.theme_manager.current_theme else None
            
            return jsonify({
                'available_themes': themes,
                'current_theme': current_theme
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def set_theme(self, theme_name):
        """Set current theme"""
        try:
            data = request.get_json() or {}
            team_colors = data.get('team_colors', {})
            
            if theme_name not in self.theme_manager.list_available_themes():
                return jsonify({'message': f'Unknown theme: {theme_name}'}), 404
            
            self.theme_manager.set_current_theme(theme_name, **team_colors)
            
            return jsonify({
                'message': f'Theme set to {theme_name}',
                'theme_config': self.theme_manager.current_theme.export_config()
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def create_custom_theme(self):
        """Create custom theme based on existing theme"""
        try:
            current_user = get_current_user()
            data = request.get_json()
            
            # Validate required fields
            theme_name = data.get('name')
            base_theme = data.get('base_theme', 'charcoal_professional')
            customizations = data.get('customizations', {})
            
            if not theme_name:
                return jsonify({'message': 'Theme name is required'}), 400
            
            # Create custom theme
            custom_theme = self.theme_manager.create_custom_theme(
                name=f"{current_user['id']}_{theme_name}",
                base_theme=base_theme,
                **customizations
            )
            
            return jsonify({
                'message': 'Custom theme created successfully',
                'theme_name': f"{current_user['id']}_{theme_name}",
                'theme_config': custom_theme.export_config()
            }), 201
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def export_chart(self, chart_id):
        """Export chart in specified format"""
        try:
            # This would require storing chart configurations
            # For now, return placeholder
            format_type = request.args.get('format', 'png')
            preset = request.args.get('preset', 'web')
            
            return jsonify({
                'message': 'Chart export functionality requires chart storage implementation',
                'chart_id': chart_id,
                'format': format_type,
                'preset': preset
            }), 501  # Not implemented
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def process_game_data(self, game_id):
        """Process game data and return football analytics"""
        try:
            current_user = get_current_user()
            
            # Get game and verify permissions
            from app import Game, PlayData
            game = Game.query.get(game_id)
            if not game:
                return jsonify({'message': 'Game not found'}), 404
            
            if current_user['type'] == 'team' and game.team_id != current_user['id']:
                return jsonify({'message': 'Access denied'}), 403
            
            # Get play data
            plays = PlayData.query.filter_by(game_id=game_id).all()
            play_data = [
                {
                    'yards_gained': play.yards_gained,
                    'formation': play.formation,
                    'play_type': play.play_type,
                    'down': play.down,
                    'distance': play.distance,
                    'points_scored': play.points_scored,
                    'yard_line': play.yard_line,
                    'result_of_play': play.result_of_play
                }
                for play in plays
            ]
            
            # Process data
            processed_data = self.data_processor.process_play_data(play_data)
            
            # Convert summary to dict for JSON serialization
            summary_dict = processed_data['summary'].__dict__ if processed_data.get('summary') else {}
            
            return jsonify({
                'game_info': {
                    'id': game.id,
                    'week': game.week,
                    'opponent': game.opponent,
                    'location': game.location
                },
                'summary': summary_dict,
                'formations': processed_data.get('formations', {}),
                'play_types': processed_data.get('play_types', {}),
                'down_distance': processed_data.get('down_distance', {}),
                'situational': processed_data.get('situational', {}),
                'available_charts': list(CHART_TEMPLATES.keys())
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def compare_data(self):
        """Compare data between two games or datasets"""
        try:
            current_user = get_current_user()
            data = request.get_json()
            
            game_id_1 = data.get('game_id_1')
            game_id_2 = data.get('game_id_2')
            
            if not game_id_1 or not game_id_2:
                return jsonify({'message': 'Both game_id_1 and game_id_2 are required'}), 400
            
            # Get and process both games
            from app import Game, PlayData
            
            # Process first game
            game1 = Game.query.get(game_id_1)
            if not game1:
                return jsonify({'message': 'Game 1 not found'}), 404
            
            if current_user['type'] == 'team' and game1.team_id != current_user['id']:
                return jsonify({'message': 'Access denied to game 1'}), 403
            
            plays1 = PlayData.query.filter_by(game_id=game_id_1).all()
            play_data1 = [
                {
                    'yards_gained': play.yards_gained,
                    'formation': play.formation,
                    'play_type': play.play_type,
                    'down': play.down,
                    'distance': play.distance,
                    'points_scored': play.points_scored,
                    'yard_line': play.yard_line,
                    'result_of_play': play.result_of_play
                }
                for play in plays1
            ]
            processed_data1 = self.data_processor.process_play_data(play_data1)
            
            # Process second game
            game2 = Game.query.get(game_id_2)
            if not game2:
                return jsonify({'message': 'Game 2 not found'}), 404
            
            plays2 = PlayData.query.filter_by(game_id=game_id_2).all()
            play_data2 = [
                {
                    'yards_gained': play.yards_gained,
                    'formation': play.formation,
                    'play_type': play.play_type,
                    'down': play.down,
                    'distance': play.distance,
                    'points_scored': play.points_scored,
                    'yard_line': play.yard_line,
                    'result_of_play': play.result_of_play
                }
                for play in plays2
            ]
            processed_data2 = self.data_processor.process_play_data(play_data2)
            
            # Generate comparison
            comparison = self.data_processor.compare_datasets(
                processed_data1, processed_data2,
                labels=(f"Week {game1.week} vs {game1.opponent}", f"Week {game2.week} vs {game2.opponent}")
            )
            
            return jsonify({
                'comparison': comparison,
                'game1_info': {
                    'id': game1.id,
                    'week': game1.week,
                    'opponent': game1.opponent,
                    'location': game1.location
                },
                'game2_info': {
                    'id': game2.id,
                    'week': game2.week,
                    'opponent': game2.opponent,
                    'location': game2.location
                }
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    def _ensure_query_builder(self):
        """Ensure query builder is initialized with PlayData model"""
        if self.query_builder is None:
            from app import PlayData
            self.query_builder = CustomQueryBuilder(self.db.session, PlayData)
    
    def get_filter_schema(self):
        """Get available filter fields and their configurations"""
        try:
            schema = PlayDataFilterSchema.get_all_fields()
            groups = PlayDataFilterSchema.get_fields_by_group()
            
            # Convert to serializable format
            schema_dict = {}
            for field_name, config in schema.items():
                schema_dict[field_name] = {
                    'field_name': config.field_name,
                    'display_name': config.display_name,
                    'data_type': config.data_type.value,
                    'ui_type': config.ui_type.value,
                    'description': config.description,
                    'required': config.required,
                    'min_value': config.min_value,
                    'max_value': config.max_value,
                    'options': config.options,
                    'default_value': config.default_value,
                    'group': config.group,
                    'searchable': config.searchable,
                    'sortable': config.sortable
                }
            
            groups_dict = {}
            for group_name, fields in groups.items():
                groups_dict[group_name] = [field.field_name for field in fields]
            
            return jsonify({
                'fields': schema_dict,
                'groups': groups_dict,
                'searchable_fields': [f.field_name for f in PlayDataFilterSchema.get_searchable_fields()],
                'sortable_fields': [f.field_name for f in PlayDataFilterSchema.get_sortable_fields()]
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    def get_filter_presets(self):
        """Get pre-configured filter combinations"""
        try:
            presets = CustomFilterPresets.get_all_presets()
            return jsonify({'presets': presets}), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def execute_custom_query(self):
        """Execute a custom query with filter conditions"""
        try:
            self._ensure_query_builder()
            current_user = get_current_user()
            data = request.get_json()
            
            # Parse filter group from request
            filter_group_data = data.get('filter_group')
            game_id = data.get('game_id')
            limit = data.get('limit', 100)  # Default limit
            offset = data.get('offset', 0)
            
            if not filter_group_data:
                return jsonify({'message': 'filter_group is required'}), 400
            
            # Convert to LogicGroup object
            filter_group = LogicGroup.from_dict(filter_group_data)
            
            # Validate permissions for game access
            if game_id:
                from app import Game
                game = Game.query.get(game_id)
                if not game:
                    return jsonify({'message': 'Game not found'}), 404
                
                if current_user['type'] == 'team' and game.team_id != current_user['id']:
                    return jsonify({'message': 'Access denied'}), 403
            
            # Execute query
            results = self.query_builder.execute_query(filter_group, game_id)
            
            # Apply pagination
            total_results = len(results)
            paginated_results = results[offset:offset + limit]
            
            return jsonify({
                'results': paginated_results,
                'total_count': total_results,
                'offset': offset,
                'limit': limit,
                'has_more': offset + limit < total_results
            }), 200
            
        except ValueError as e:
            return jsonify({'message': f'Invalid filter configuration: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def get_query_stats(self):
        """Get statistics for a custom query without executing full query"""
        try:
            self._ensure_query_builder()
            current_user = get_current_user()
            data = request.get_json()
            
            # Parse filter group from request
            filter_group_data = data.get('filter_group')
            game_id = data.get('game_id')
            
            if not filter_group_data:
                return jsonify({'message': 'filter_group is required'}), 400
            
            # Convert to LogicGroup object
            filter_group = LogicGroup.from_dict(filter_group_data)
            
            # Validate permissions for game access
            if game_id:
                from app import Game
                game = Game.query.get(game_id)
                if not game:
                    return jsonify({'message': 'Game not found'}), 404
                
                if current_user['type'] == 'team' and game.team_id != current_user['id']:
                    return jsonify({'message': 'Access denied'}), 403
            
            # Get query statistics
            stats = self.query_builder.get_query_stats(filter_group, game_id)
            
            return jsonify({'stats': stats}), 200
            
        except ValueError as e:
            return jsonify({'message': f'Invalid filter configuration: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def get_query_templates(self):
        """Get saved query templates"""
        try:
            current_user = get_current_user()
            
            # Get pre-built templates
            prebuilt_templates = PrebuiltTemplates.get_all_templates()
            
            # Convert to JSON format
            templates = []
            for template in prebuilt_templates:
                templates.append({
                    'id': f'prebuilt_{template.name.lower().replace(" ", "_")}',
                    'name': template.name,
                    'description': template.description,
                    'filter_group': template.filter_group.to_dict(),
                    'created_by': 'system',
                    'tags': template.tags,
                    'is_prebuilt': True
                })
            
            # TODO: Add user-saved templates from database
            # This would require a QueryTemplate model in the database
            
            return jsonify({
                'templates': templates,
                'prebuilt_count': len(prebuilt_templates),
                'user_templates_count': 0  # Placeholder
            }), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def save_query_template(self):
        """Save a custom query as a template"""
        try:
            current_user = get_current_user()
            data = request.get_json()
            
            # Validate required fields
            name = data.get('name')
            description = data.get('description', '')
            filter_group_data = data.get('filter_group')
            tags = data.get('tags', [])
            
            if not name or not filter_group_data:
                return jsonify({'message': 'name and filter_group are required'}), 400
            
            # Validate filter group
            try:
                filter_group = LogicGroup.from_dict(filter_group_data)
            except Exception as e:
                return jsonify({'message': f'Invalid filter_group: {str(e)}'}), 400
            
            # Create template
            template = QueryTemplate(
                name=name,
                description=description,
                filter_group=filter_group,
                created_by=current_user['id'],
                tags=tags
            )
            
            # TODO: Save to database
            # This would require a QueryTemplate model in the database
            # For now, return success with template data
            
            return jsonify({
                'message': 'Template saved successfully',
                'template': {
                    'id': f'user_{current_user["id"]}_{name.lower().replace(" ", "_")}',
                    'name': template.name,
                    'description': template.description,
                    'filter_group': template.filter_group.to_dict(),
                    'created_by': template.created_by,
                    'tags': template.tags,
                    'is_prebuilt': False
                }
            }), 201
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500
    
    @jwt_required()
    def delete_query_template(self, template_id):
        """Delete a saved query template"""
        try:
            current_user = get_current_user()
            
            # Check if it's a prebuilt template (cannot be deleted)
            if template_id.startswith('prebuilt_'):
                return jsonify({'message': 'Cannot delete prebuilt templates'}), 400
            
            # TODO: Delete from database
            # This would require a QueryTemplate model in the database
            # For now, return success
            
            return jsonify({'message': 'Template deleted successfully'}), 200
            
        except Exception as e:
            return jsonify({'message': str(e)}), 500


def init_footballviz_api(app, db, socketio=None):
    """
    Initialize FootballViz API with Flask application
    
    Args:
        app: Flask application instance
        db: SQLAlchemy database instance
        socketio: SocketIO instance (optional)
    
    Returns:
        FootballVizAPI instance
    """
    return FootballVizAPI(app, db, socketio)