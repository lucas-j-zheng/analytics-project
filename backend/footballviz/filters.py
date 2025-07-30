"""
FootballViz Filter Configuration System

Define available filter fields, data types, validation rules, and UI configurations
for the custom query builder interface.
"""

from typing import Dict, List, Any, Optional, Union
from enum import Enum
from dataclasses import dataclass


class FilterFieldType(Enum):
    """Data types for filter fields"""
    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    BOOLEAN = "boolean"
    ENUM = "enum"
    DATETIME = "datetime"


class FilterUIType(Enum):
    """UI component types for different filters"""
    TEXT_INPUT = "text_input"
    NUMBER_INPUT = "number_input"
    RANGE_SLIDER = "range_slider"
    DROPDOWN = "dropdown"
    MULTI_SELECT = "multi_select"
    CHECKBOX = "checkbox"
    DATE_PICKER = "date_picker"


@dataclass
class FilterFieldConfig:
    """Configuration for a single filter field"""
    field_name: str
    display_name: str
    data_type: FilterFieldType
    ui_type: FilterUIType
    description: str
    required: bool = False
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    options: Optional[List[Dict[str, Any]]] = None
    default_value: Optional[Any] = None
    validation_rules: Optional[Dict[str, Any]] = None
    group: Optional[str] = None
    searchable: bool = False
    sortable: bool = False


class PlayDataFilterSchema:
    """Schema definition for PlayData model filters"""
    
    @staticmethod
    def get_all_fields() -> Dict[str, FilterFieldConfig]:
        """Get all available filter fields for PlayData"""
        return {
            # Game Context Fields
            'game_id': FilterFieldConfig(
                field_name='game_id',
                display_name='Game',
                data_type=FilterFieldType.INTEGER,
                ui_type=FilterUIType.DROPDOWN,
                description='Select specific game to analyze',
                group='Game Context'
            ),
            
            'play_id': FilterFieldConfig(
                field_name='play_id',
                display_name='Play Number',
                data_type=FilterFieldType.INTEGER,
                ui_type=FilterUIType.NUMBER_INPUT,
                description='Sequential play number in the game',
                min_value=1,
                group='Game Context',
                sortable=True
            ),
            
            # Down and Distance
            'down': FilterFieldConfig(
                field_name='down',
                display_name='Down',
                data_type=FilterFieldType.ENUM,
                ui_type=FilterUIType.MULTI_SELECT,
                description='Which down (1st, 2nd, 3rd, 4th)',
                options=[
                    {'value': 1, 'label': '1st Down'},
                    {'value': 2, 'label': '2nd Down'},
                    {'value': 3, 'label': '3rd Down'},
                    {'value': 4, 'label': '4th Down'}
                ],
                group='Situation'
            ),
            
            'distance': FilterFieldConfig(
                field_name='distance',
                display_name='Distance to Go',
                data_type=FilterFieldType.INTEGER,
                ui_type=FilterUIType.RANGE_SLIDER,
                description='Yards needed for first down',
                min_value=1,
                max_value=30,
                group='Situation',
                sortable=True
            ),
            
            # Field Position
            'yard_line': FilterFieldConfig(
                field_name='yard_line',
                display_name='Yard Line',
                data_type=FilterFieldType.INTEGER,
                ui_type=FilterUIType.RANGE_SLIDER,
                description='Field position (0-100, own goal line to opponent goal line)',
                min_value=0,
                max_value=100,
                group='Field Position',
                sortable=True
            ),
            
            # Formation and Play Details
            'formation': FilterFieldConfig(
                field_name='formation',
                display_name='Formation',
                data_type=FilterFieldType.ENUM,
                ui_type=FilterUIType.MULTI_SELECT,
                description='Offensive formation used',
                options=PlayDataFilterSchema._get_formation_options(),
                group='Play Details',
                searchable=True
            ),
            
            'play_type': FilterFieldConfig(
                field_name='play_type',
                display_name='Play Type',
                data_type=FilterFieldType.ENUM,
                ui_type=FilterUIType.MULTI_SELECT,
                description='Type of play (Pass, Run, Special)',
                options=[
                    {'value': 'Pass', 'label': 'Pass'},
                    {'value': 'Run', 'label': 'Run'},
                    {'value': 'Special', 'label': 'Special Teams'},
                    {'value': 'Punt', 'label': 'Punt'},
                    {'value': 'Field Goal', 'label': 'Field Goal'},
                    {'value': 'Kickoff', 'label': 'Kickoff'}
                ],
                group='Play Details'
            ),
            
            'play_name': FilterFieldConfig(
                field_name='play_name',
                display_name='Play Name',
                data_type=FilterFieldType.STRING,
                ui_type=FilterUIType.TEXT_INPUT,
                description='Specific play call or route combination',
                group='Play Details',
                searchable=True
            ),
            
            # Results
            'yards_gained': FilterFieldConfig(
                field_name='yards_gained',
                display_name='Yards Gained',
                data_type=FilterFieldType.INTEGER,
                ui_type=FilterUIType.RANGE_SLIDER,
                description='Net yards gained on the play',
                min_value=-20,
                max_value=80,
                group='Results',
                sortable=True
            ),
            
            'result_of_play': FilterFieldConfig(
                field_name='result_of_play',
                display_name='Result',
                data_type=FilterFieldType.STRING,
                ui_type=FilterUIType.TEXT_INPUT,
                description='Outcome description (completion, tackle, fumble, etc.)',
                group='Results',
                searchable=True
            )
        }
    
    @staticmethod
    def _get_formation_options() -> List[Dict[str, Any]]:
        """Get common football formation options"""
        return [
            {'value': 'I-Formation', 'label': 'I-Formation'},
            {'value': 'Shotgun', 'label': 'Shotgun'},
            {'value': 'Pistol', 'label': 'Pistol'},
            {'value': 'Singleback', 'label': 'Singleback'},
            {'value': 'Wildcat', 'label': 'Wildcat'},
            {'value': 'Empty', 'label': 'Empty Backfield'},
            {'value': 'Goal Line', 'label': 'Goal Line'},
            {'value': 'Spread', 'label': 'Spread'},
            {'value': 'Wing-T', 'label': 'Wing-T'},
            {'value': 'Power-I', 'label': 'Power-I'}
        ]
    
    @staticmethod
    def get_fields_by_group() -> Dict[str, List[FilterFieldConfig]]:
        """Get fields organized by group"""
        all_fields = PlayDataFilterSchema.get_all_fields()
        groups = {}
        
        for field in all_fields.values():
            group_name = field.group or 'Other'
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(field)
        
        return groups
    
    @staticmethod
    def get_searchable_fields() -> List[FilterFieldConfig]:
        """Get fields that support text search"""
        all_fields = PlayDataFilterSchema.get_all_fields()
        return [field for field in all_fields.values() if field.searchable]
    
    @staticmethod
    def get_sortable_fields() -> List[FilterFieldConfig]:
        """Get fields that support sorting"""
        all_fields = PlayDataFilterSchema.get_all_fields()
        return [field for field in all_fields.values() if field.sortable]


class FilterValidation:
    """Validation utilities for filter values"""
    
    @staticmethod
    def validate_field_value(field_config: FilterFieldConfig, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a field value against its configuration
        
        Returns:
            tuple: (is_valid, error_message)
        """
        if value is None and not field_config.required:
            return True, None
        
        if value is None and field_config.required:
            return False, f"{field_config.display_name} is required"
        
        # Type validation
        if field_config.data_type == FilterFieldType.INTEGER:
            if not isinstance(value, int):
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    return False, f"{field_config.display_name} must be an integer"
        
        elif field_config.data_type == FilterFieldType.FLOAT:
            if not isinstance(value, (int, float)):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    return False, f"{field_config.display_name} must be a number"
        
        elif field_config.data_type == FilterFieldType.STRING:
            if not isinstance(value, str):
                return False, f"{field_config.display_name} must be a string"
        
        elif field_config.data_type == FilterFieldType.ENUM:
            if field_config.options:
                valid_values = [opt['value'] for opt in field_config.options]
                if isinstance(value, list):
                    # Multi-select validation
                    for v in value:
                        if v not in valid_values:
                            return False, f"Invalid value '{v}' for {field_config.display_name}"
                else:
                    # Single value validation
                    if value not in valid_values:
                        return False, f"Invalid value '{value}' for {field_config.display_name}"
        
        # Range validation
        if field_config.min_value is not None and isinstance(value, (int, float)):
            if value < field_config.min_value:
                return False, f"{field_config.display_name} must be at least {field_config.min_value}"
        
        if field_config.max_value is not None and isinstance(value, (int, float)):
            if value > field_config.max_value:
                return False, f"{field_config.display_name} must be at most {field_config.max_value}"
        
        return True, None
    
    @staticmethod
    def validate_filter_combination(conditions: List[Dict[str, Any]]) -> tuple[bool, Optional[str]]:
        """
        Validate that a combination of filters makes sense
        
        Args:
            conditions: List of filter condition dictionaries
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Check for conflicting conditions
        field_conditions = {}
        for condition in conditions:
            field = condition.get('field')
            operator = condition.get('operator')
            value = condition.get('value')
            
            if field in field_conditions:
                field_conditions[field].append((operator, value))
            else:
                field_conditions[field] = [(operator, value)]
        
        # Look for logical conflicts
        for field, conditions_list in field_conditions.items():
            if len(conditions_list) > 1:
                # Check for impossible combinations
                equals_values = []
                not_equals_values = []
                
                for op, val in conditions_list:
                    if op == 'equals':
                        equals_values.append(val)
                    elif op == 'not_equals':
                        not_equals_values.append(val)
                
                # Multiple equals conditions for same field
                if len(equals_values) > 1:
                    return False, f"Cannot have multiple equal conditions for {field}"
                
                # Equals and not_equals conflict
                if equals_values and not_equals_values:
                    for eq_val in equals_values:
                        if eq_val in not_equals_values:
                            return False, f"Conflicting conditions for {field}: equals and not equals same value"
        
        return True, None


class CustomFilterPresets:
    """Pre-configured filter combinations for common scenarios"""
    
    @staticmethod
    def get_situation_presets() -> Dict[str, Dict[str, Any]]:
        """Get preset filter combinations for common game situations"""
        return {
            'red_zone': {
                'name': 'Red Zone',
                'description': 'Plays inside the 20-yard line',
                'filters': [
                    {'field': 'yard_line', 'operator': 'greater_than_or_equal', 'value': 80}
                ],
                'icon': '🔴',
                'color': '#EF4444'
            },
            
            'goal_line': {
                'name': 'Goal Line',
                'description': 'Plays inside the 5-yard line',
                'filters': [
                    {'field': 'yard_line', 'operator': 'greater_than_or_equal', 'value': 95}
                ],
                'icon': '🎯',
                'color': '#DC2626'
            },
            
            'third_down': {
                'name': 'Third Down',
                'description': 'All third down situations',
                'filters': [
                    {'field': 'down', 'operator': 'equals', 'value': 3}
                ],
                'icon': '3️⃣',
                'color': '#F59E0B'
            },
            
            'short_yardage': {
                'name': 'Short Yardage',
                'description': '3rd or 4th down with ≤2 yards needed',
                'filters': [
                    {'field': 'down', 'operator': 'in', 'value': [3, 4]},
                    {'field': 'distance', 'operator': 'less_than_or_equal', 'value': 2}
                ],
                'icon': '💪',
                'color': '#8B5CF6'
            },
            
            'long_yardage': {
                'name': 'Long Yardage',
                'description': 'Situations with 10+ yards needed',
                'filters': [
                    {'field': 'distance', 'operator': 'greater_than_or_equal', 'value': 10}
                ],
                'icon': '📏',
                'color': '#06B6D4'
            },
            
            'explosive_plays': {
                'name': 'Explosive Plays',
                'description': 'Plays gaining 20+ yards',
                'filters': [
                    {'field': 'yards_gained', 'operator': 'greater_than_or_equal', 'value': 20}
                ],
                'icon': '💥',
                'color': '#10B981'
            },
            
            'passing_downs': {
                'name': 'Passing Downs',
                'description': 'Obvious passing situations (2nd/3rd & long)',
                'filters': [
                    {'field': 'down', 'operator': 'in', 'value': [2, 3]},
                    {'field': 'distance', 'operator': 'greater_than_or_equal', 'value': 7}
                ],
                'icon': '🏈',
                'color': '#3B82F6'
            },
            
            'running_downs': {
                'name': 'Running Downs',
                'description': 'Short yardage and early down situations',
                'filters': [
                    {'field': 'down', 'operator': 'in', 'value': [1, 2]},
                    {'field': 'distance', 'operator': 'less_than_or_equal', 'value': 5}
                ],
                'icon': '🏃',
                'color': '#EF4444'
            }
        }
    
    @staticmethod
    def get_formation_presets() -> Dict[str, Dict[str, Any]]:
        """Get preset filters based on formations"""
        return {
            'shotgun_formations': {
                'name': 'Shotgun Formations',
                'description': 'All shotgun-based formations',
                'filters': [
                    {'field': 'formation', 'operator': 'contains', 'value': 'Shotgun'}
                ],
                'icon': '🔫',
                'color': '#8B5CF6'
            },
            
            'heavy_formations': {
                'name': 'Heavy Formations',
                'description': 'Goal line and power formations',
                'filters': [
                    {'field': 'formation', 'operator': 'in', 'value': ['Goal Line', 'I-Formation', 'Power-I']}
                ],
                'icon': '🏋️',
                'color': '#EF4444'
            },
            
            'spread_formations': {
                'name': 'Spread Formations',
                'description': 'Spread and empty backfield sets',
                'filters': [
                    {'field': 'formation', 'operator': 'in', 'value': ['Spread', 'Empty']}
                ],
                'icon': '↔️',
                'color': '#06B6D4'
            }
        }
    
    @staticmethod
    def get_all_presets() -> Dict[str, Dict[str, Any]]:
        """Get all available presets"""
        return {
            **CustomFilterPresets.get_situation_presets(),
            **CustomFilterPresets.get_formation_presets()
        }