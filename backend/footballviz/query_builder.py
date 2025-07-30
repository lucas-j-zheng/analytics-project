"""
FootballViz Custom Query Builder

Dynamic SQL query generation service for complex football data analysis:
- Support for logical operators (AND, OR, NOT)
- Range queries, text matching, multi-value selections
- Type-safe query construction with validation
"""

from typing import Dict, List, Any, Optional, Union, Tuple
from enum import Enum
from sqlalchemy import and_, or_, not_, func, text
from sqlalchemy.orm.query import Query


class FilterOperator(Enum):
    """Supported filter operators"""
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    BETWEEN = "between"
    IN = "in"
    NOT_IN = "not_in"
    CONTAINS = "contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


class LogicOperator(Enum):
    """Logical operators for combining conditions"""
    AND = "and"
    OR = "or"
    NOT = "not"


class FilterCondition:
    """Individual filter condition"""
    
    def __init__(self, field: str, operator: FilterOperator, value: Any = None):
        self.field = field
        self.operator = operator
        self.value = value
        self.validate()
    
    def validate(self):
        """Validate the filter condition"""
        if self.operator in [FilterOperator.IS_NULL, FilterOperator.IS_NOT_NULL]:
            if self.value is not None:
                raise ValueError(f"NULL operators should not have a value")
        elif self.operator == FilterOperator.BETWEEN:
            if not isinstance(self.value, (list, tuple)) or len(self.value) != 2:
                raise ValueError("BETWEEN operator requires a list/tuple of 2 values")
        elif self.operator in [FilterOperator.IN, FilterOperator.NOT_IN]:
            if not isinstance(self.value, (list, tuple)):
                raise ValueError("IN/NOT_IN operators require a list/tuple of values")
        elif self.value is None:
            raise ValueError(f"Operator {self.operator.value} requires a value")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'field': self.field,
            'operator': self.operator.value,
            'value': self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterCondition':
        """Create from dictionary representation"""
        return cls(
            field=data['field'],
            operator=FilterOperator(data['operator']),
            value=data.get('value')
        )


class LogicGroup:
    """Group of filter conditions with logical operators"""
    
    def __init__(self, operator: LogicOperator = LogicOperator.AND):
        self.operator = operator
        self.conditions: List[Union[FilterCondition, 'LogicGroup']] = []
    
    def add_condition(self, condition: Union[FilterCondition, 'LogicGroup']):
        """Add a condition or nested group"""
        self.conditions.append(condition)
    
    def add_filter(self, field: str, operator: FilterOperator, value: Any = None):
        """Add a filter condition directly"""
        condition = FilterCondition(field, operator, value)
        self.add_condition(condition)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'operator': self.operator.value,
            'conditions': [
                cond.to_dict() if isinstance(cond, FilterCondition) else cond.to_dict()
                for cond in self.conditions
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LogicGroup':
        """Create from dictionary representation"""
        group = cls(LogicOperator(data['operator']))
        for cond_data in data['conditions']:
            if 'operator' in cond_data and cond_data['operator'] in ['and', 'or', 'not']:
                # It's a nested group
                group.add_condition(cls.from_dict(cond_data))
            else:
                # It's a filter condition
                group.add_condition(FilterCondition.from_dict(cond_data))
        return group


class CustomQueryBuilder:
    """Main query builder service"""
    
    def __init__(self, db_session, play_data_model):
        self.db_session = db_session
        self.play_data_model = play_data_model
        self.base_query = db_session.query(play_data_model)
    
    def build_query(self, filter_group: LogicGroup, game_id: Optional[int] = None) -> Query:
        """Build SQLAlchemy query from filter group"""
        query = self.base_query
        
        # Add game filter if specified
        if game_id:
            query = query.filter(self.play_data_model.game_id == game_id)
        
        # Apply custom filters
        if filter_group.conditions:
            query = query.filter(self._build_where_clause(filter_group))
        
        return query
    
    def _build_where_clause(self, group: LogicGroup):
        """Build WHERE clause from logic group"""
        if not group.conditions:
            return True
        
        clauses = []
        for condition in group.conditions:
            if isinstance(condition, FilterCondition):
                clauses.append(self._build_condition_clause(condition))
            elif isinstance(condition, LogicGroup):
                clauses.append(self._build_where_clause(condition))
        
        if group.operator == LogicOperator.AND:
            return and_(*clauses)
        elif group.operator == LogicOperator.OR:
            return or_(*clauses)
        elif group.operator == LogicOperator.NOT:
            return not_(and_(*clauses))
        
        return and_(*clauses)  # Default to AND
    
    def _build_condition_clause(self, condition: FilterCondition):
        """Build individual condition clause"""
        field = getattr(self.play_data_model, condition.field)
        
        if condition.operator == FilterOperator.EQUALS:
            return field == condition.value
        elif condition.operator == FilterOperator.NOT_EQUALS:
            return field != condition.value
        elif condition.operator == FilterOperator.GREATER_THAN:
            return field > condition.value
        elif condition.operator == FilterOperator.GREATER_THAN_OR_EQUAL:
            return field >= condition.value
        elif condition.operator == FilterOperator.LESS_THAN:
            return field < condition.value
        elif condition.operator == FilterOperator.LESS_THAN_OR_EQUAL:
            return field <= condition.value
        elif condition.operator == FilterOperator.BETWEEN:
            return field.between(condition.value[0], condition.value[1])
        elif condition.operator == FilterOperator.IN:
            return field.in_(condition.value)
        elif condition.operator == FilterOperator.NOT_IN:
            return ~field.in_(condition.value)
        elif condition.operator == FilterOperator.CONTAINS:
            return field.contains(condition.value)
        elif condition.operator == FilterOperator.STARTS_WITH:
            return field.startswith(condition.value)
        elif condition.operator == FilterOperator.ENDS_WITH:
            return field.endswith(condition.value)
        elif condition.operator == FilterOperator.IS_NULL:
            return field.is_(None)
        elif condition.operator == FilterOperator.IS_NOT_NULL:
            return field.isnot(None)
        
        raise ValueError(f"Unsupported operator: {condition.operator}")
    
    def execute_query(self, filter_group: LogicGroup, game_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Execute query and return results"""
        query = self.build_query(filter_group, game_id)
        results = query.all()
        
        # Convert to dictionaries
        return [self._row_to_dict(row) for row in results]
    
    def get_query_stats(self, filter_group: LogicGroup, game_id: Optional[int] = None) -> Dict[str, Any]:
        """Get statistics about the query results"""
        query = self.build_query(filter_group, game_id)
        
        total_count = query.count()
        
        if total_count == 0:
            return {
                'total_plays': 0,
                'avg_yards_gained': 0,
                'success_rate': 0,
                'formations_count': 0,
                'play_types_count': 0
            }
        
        # Calculate statistics
        avg_yards = query.with_entities(func.avg(self.play_data_model.yards_gained)).scalar() or 0
        
        # Success rate (plays with positive yards)
        successful_plays = query.filter(self.play_data_model.yards_gained > 0).count()
        success_rate = (successful_plays / total_count) * 100 if total_count > 0 else 0
        
        # Unique formations and play types
        formations_count = query.with_entities(self.play_data_model.formation).distinct().count()
        play_types_count = query.with_entities(self.play_data_model.play_type).distinct().count()
        
        return {
            'total_plays': total_count,
            'avg_yards_gained': round(avg_yards, 2),
            'success_rate': round(success_rate, 1),
            'formations_count': formations_count,
            'play_types_count': play_types_count
        }
    
    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert SQLAlchemy row to dictionary"""
        return {
            'id': row.id,
            'game_id': row.game_id,
            'play_id': row.play_id,
            'down': row.down,
            'distance': row.distance,
            'yard_line': row.yard_line,
            'formation': row.formation,
            'play_type': row.play_type,
            'play_name': row.play_name,
            'result_of_play': row.result_of_play,
            'yards_gained': row.yards_gained
        }


class QueryTemplate:
    """Saved query template for reuse"""
    
    def __init__(self, name: str, description: str, filter_group: LogicGroup, 
                 created_by: Optional[str] = None, tags: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.filter_group = filter_group
        self.created_by = created_by
        self.tags = tags or []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            'name': self.name,
            'description': self.description,
            'filter_group': self.filter_group.to_dict(),
            'created_by': self.created_by,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryTemplate':
        """Create from dictionary representation"""
        return cls(
            name=data['name'],
            description=data['description'],
            filter_group=LogicGroup.from_dict(data['filter_group']),
            created_by=data.get('created_by'),
            tags=data.get('tags', [])
        )


class PrebuiltTemplates:
    """Collection of pre-built query templates for common football scenarios"""
    
    @staticmethod
    def red_zone_analysis() -> QueryTemplate:
        """Red zone offensive analysis"""
        group = LogicGroup(LogicOperator.AND)
        group.add_filter('yard_line', FilterOperator.GREATER_THAN_OR_EQUAL, 80)
        
        return QueryTemplate(
            name="Red Zone Analysis",
            description="Analyze offensive performance in the red zone (20-yard line and closer)",
            filter_group=group,
            tags=['red-zone', 'offense', 'scoring']
        )
    
    @staticmethod
    def third_down_situations() -> QueryTemplate:
        """Third down conversion analysis"""
        group = LogicGroup(LogicOperator.AND)
        group.add_filter('down', FilterOperator.EQUALS, 3)
        group.add_filter('distance', FilterOperator.LESS_THAN_OR_EQUAL, 10)
        
        return QueryTemplate(
            name="Third Down Situations",
            description="Analyze third down conversion attempts with manageable distance",
            filter_group=group,
            tags=['third-down', 'conversions', 'critical-situations']
        )
    
    @staticmethod
    def explosive_plays() -> QueryTemplate:
        """Explosive offensive plays"""
        group = LogicGroup(LogicOperator.OR)
        group.add_filter('yards_gained', FilterOperator.GREATER_THAN_OR_EQUAL, 20)
        
        # Could add more conditions for explosive plays (TDs, etc.)
        
        return QueryTemplate(
            name="Explosive Plays",
            description="Plays that gained 20+ yards or resulted in touchdowns",
            filter_group=group,
            tags=['explosive-plays', 'big-gains', 'offense']
        )
    
    @staticmethod
    def short_yardage() -> QueryTemplate:
        """Short yardage situations"""
        group = LogicGroup(LogicOperator.AND)
        group.add_filter('distance', FilterOperator.LESS_THAN_OR_EQUAL, 2)
        
        down_group = LogicGroup(LogicOperator.OR)
        down_group.add_filter('down', FilterOperator.EQUALS, 3)
        down_group.add_filter('down', FilterOperator.EQUALS, 4)
        
        group.add_condition(down_group)
        
        return QueryTemplate(
            name="Short Yardage",
            description="Third and fourth down situations with 2 yards or less needed",
            filter_group=group,
            tags=['short-yardage', 'power-football', 'critical-downs']
        )
    
    @staticmethod
    def passing_plays() -> QueryTemplate:
        """All passing plays analysis"""
        group = LogicGroup(LogicOperator.AND)
        group.add_filter('play_type', FilterOperator.EQUALS, 'Pass')
        
        return QueryTemplate(
            name="Passing Plays",
            description="All passing play attempts for aerial attack analysis",
            filter_group=group,
            tags=['passing', 'offense', 'aerial']
        )
    
    @staticmethod
    def running_plays() -> QueryTemplate:
        """All running plays analysis"""
        group = LogicGroup(LogicOperator.AND)
        group.add_filter('play_type', FilterOperator.EQUALS, 'Run')
        
        return QueryTemplate(
            name="Running Plays",
            description="All running play attempts for ground game analysis",
            filter_group=group,
            tags=['running', 'offense', 'ground-game']
        )
    
    @staticmethod
    def get_all_templates() -> List[QueryTemplate]:
        """Get all pre-built templates"""
        return [
            PrebuiltTemplates.red_zone_analysis(),
            PrebuiltTemplates.third_down_situations(),
            PrebuiltTemplates.explosive_plays(),
            PrebuiltTemplates.short_yardage(),
            PrebuiltTemplates.passing_plays(),
            PrebuiltTemplates.running_plays()
        ]