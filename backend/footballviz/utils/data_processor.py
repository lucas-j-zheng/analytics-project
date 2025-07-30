"""
FootballViz Data Processing Utilities

Specialized data processing functions for football analytics:
- Play data transformation and aggregation
- Efficiency and performance calculations
- Situational analysis utilities
"""

from typing import Dict, List, Any, Optional, Tuple, Union
import numpy as np
from collections import defaultdict, Counter
from dataclasses import dataclass
import statistics


@dataclass
class PlayAnalysis:
    """Container for play-level analysis results"""
    total_plays: int
    total_yards: int
    total_points: int
    avg_yards_per_play: float
    success_rate: float
    explosive_plays: int
    turnovers: int


@dataclass
class EfficiencyMetrics:
    """Container for efficiency calculations"""
    overall_efficiency: float
    red_zone_efficiency: float
    third_down_efficiency: float
    goal_line_efficiency: float
    two_minute_efficiency: float


class FootballDataProcessor:
    """
    Main data processing class for football analytics
    """
    
    # Constants for football analysis
    EXPLOSIVE_PLAY_THRESHOLD = 20  # yards
    RED_ZONE_START = 80           # yard line
    GOAL_LINE_DISTANCE = 95       # yard line
    SUCCESS_THRESHOLDS = {
        1: 0.5,  # 1st down: 50% of distance
        2: 0.7,  # 2nd down: 70% of distance  
        3: 1.0,  # 3rd down: 100% of distance
        4: 1.0   # 4th down: 100% of distance
    }
    
    def __init__(self):
        self.processed_data = {}
        
    def process_play_data(self, plays: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process raw play data into analytics-ready format
        
        Args:
            plays: List of play dictionaries
            
        Returns:
            Processed data dictionary
        """
        if not plays:
            return self._empty_analysis()
        
        # Basic aggregations
        total_plays = len(plays)
        total_yards = sum(play.get('yards_gained', 0) for play in plays)
        total_points = sum(play.get('points_scored', 0) for play in plays)
        avg_yards = total_yards / total_plays if total_plays > 0 else 0
        
        # Advanced metrics
        explosive_plays = self._count_explosive_plays(plays)
        success_rate = self._calculate_success_rate(plays)
        
        # Formation analysis
        formation_stats = self._analyze_formations(plays)
        
        # Play type analysis
        play_type_stats = self._analyze_play_types(plays)
        
        # Down and distance analysis
        down_distance_stats = self._analyze_down_distance(plays)
        
        # Situational analysis
        situational_stats = self._analyze_situations(plays)
        
        return {
            'summary': PlayAnalysis(
                total_plays=total_plays,
                total_yards=total_yards,
                total_points=total_points,
                avg_yards_per_play=avg_yards,
                success_rate=success_rate,
                explosive_plays=explosive_plays,
                turnovers=0  # Would need to parse from play results
            ),
            'formations': formation_stats,
            'play_types': play_type_stats,
            'down_distance': down_distance_stats,
            'situational': situational_stats
        }
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            'summary': PlayAnalysis(0, 0, 0, 0.0, 0.0, 0, 0),
            'formations': {},
            'play_types': {},
            'down_distance': {},
            'situational': {}
        }
    
    def _count_explosive_plays(self, plays: List[Dict[str, Any]]) -> int:
        """Count explosive plays (20+ yards)"""
        return sum(1 for play in plays 
                  if play.get('yards_gained', 0) >= self.EXPLOSIVE_PLAY_THRESHOLD)
    
    def _calculate_success_rate(self, plays: List[Dict[str, Any]]) -> float:
        """Calculate overall success rate based on down and distance"""
        successful_plays = 0
        valid_plays = 0
        
        for play in plays:
            down = play.get('down')
            distance = play.get('distance')
            yards_gained = play.get('yards_gained', 0)
            
            if down and distance and down in self.SUCCESS_THRESHOLDS:
                valid_plays += 1
                success_threshold = distance * self.SUCCESS_THRESHOLDS[down]
                if yards_gained >= success_threshold:
                    successful_plays += 1
        
        return (successful_plays / valid_plays * 100) if valid_plays > 0 else 0.0
    
    def _analyze_formations(self, plays: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by formation"""
        formation_data = defaultdict(lambda: {
            'count': 0, 
            'yards': 0, 
            'points': 0,
            'successful_plays': 0,
            'explosive_plays': 0
        })
        
        for play in plays:
            formation = play.get('formation', 'Unknown')
            yards = play.get('yards_gained', 0)
            points = play.get('points_scored', 0)
            
            formation_data[formation]['count'] += 1
            formation_data[formation]['yards'] += yards
            formation_data[formation]['points'] += points
            
            if yards >= self.EXPLOSIVE_PLAY_THRESHOLD:
                formation_data[formation]['explosive_plays'] += 1
            
            # Calculate success (simplified)
            if self._is_successful_play(play):
                formation_data[formation]['successful_plays'] += 1
        
        # Calculate averages
        result = {}
        for formation, stats in formation_data.items():
            count = stats['count']
            result[formation] = {
                'count': count,
                'total_yards': stats['yards'],
                'total_points': stats['points'],
                'avg_yards': stats['yards'] / count if count > 0 else 0,
                'avg_points': stats['points'] / count if count > 0 else 0,
                'success_rate': (stats['successful_plays'] / count * 100) if count > 0 else 0,
                'explosive_rate': (stats['explosive_plays'] / count * 100) if count > 0 else 0
            }
        
        return result
    
    def _analyze_play_types(self, plays: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by play type"""
        play_type_data = defaultdict(lambda: {
            'count': 0,
            'yards': 0,
            'points': 0,
            'successful_plays': 0
        })
        
        for play in plays:
            play_type = play.get('play_type', 'Unknown')
            yards = play.get('yards_gained', 0)
            points = play.get('points_scored', 0)
            
            play_type_data[play_type]['count'] += 1
            play_type_data[play_type]['yards'] += yards
            play_type_data[play_type]['points'] += points
            
            if self._is_successful_play(play):
                play_type_data[play_type]['successful_plays'] += 1
        
        # Calculate averages and efficiency
        result = {}
        for play_type, stats in play_type_data.items():
            count = stats['count']
            result[play_type] = {
                'count': count,
                'total_yards': stats['yards'],
                'avg_yards': stats['yards'] / count if count > 0 else 0,
                'success_rate': (stats['successful_plays'] / count * 100) if count > 0 else 0,
                'points_scored': stats['points']
            }
        
        return result
    
    def _analyze_down_distance(self, plays: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by down and distance"""
        down_data = defaultdict(lambda: {
            'count': 0,
            'yards': 0,
            'successful_plays': 0,
            'conversions': 0
        })
        
        for play in plays:
            down = play.get('down')
            if down:
                down_key = f"Down {down}"
                yards = play.get('yards_gained', 0)
                distance = play.get('distance', 0)
                
                down_data[down_key]['count'] += 1
                down_data[down_key]['yards'] += yards
                
                if self._is_successful_play(play):
                    down_data[down_key]['successful_plays'] += 1
                
                # Check for conversion (gained required distance)
                if yards >= distance:
                    down_data[down_key]['conversions'] += 1
        
        # Calculate rates
        result = {}
        for down, stats in down_data.items():
            count = stats['count']
            result[down] = {
                'count': count,
                'avg_yards': stats['yards'] / count if count > 0 else 0,
                'success_rate': (stats['successful_plays'] / count * 100) if count > 0 else 0,
                'conversion_rate': (stats['conversions'] / count * 100) if count > 0 else 0
            }
        
        return result
    
    def _analyze_situations(self, plays: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze performance in key situations"""
        situations = {
            'red_zone': [],
            'goal_line': [],
            'third_down': [],
            'fourth_down': [],
            'short_yardage': []
        }
        
        for play in plays:
            yard_line = play.get('yard_line', 0)
            down = play.get('down')
            distance = play.get('distance', 0)
            
            # Categorize situations
            if yard_line >= self.RED_ZONE_START:
                situations['red_zone'].append(play)
            
            if yard_line >= self.GOAL_LINE_DISTANCE:
                situations['goal_line'].append(play)
            
            if down == 3:
                situations['third_down'].append(play)
            
            if down == 4:
                situations['fourth_down'].append(play)
            
            if distance <= 2:
                situations['short_yardage'].append(play)
        
        # Calculate situational statistics
        result = {}
        for situation, situation_plays in situations.items():
            if situation_plays:
                total_yards = sum(p.get('yards_gained', 0) for p in situation_plays)
                total_points = sum(p.get('points_scored', 0) for p in situation_plays)
                successful = sum(1 for p in situation_plays if self._is_successful_play(p))
                
                result[situation] = {
                    'attempts': len(situation_plays),
                    'total_yards': total_yards,
                    'total_points': total_points,
                    'avg_yards': total_yards / len(situation_plays),
                    'success_rate': (successful / len(situation_plays) * 100),
                    'scoring_rate': (total_points / len(situation_plays) * 100) if total_points > 0 else 0
                }
            else:
                result[situation] = {
                    'attempts': 0,
                    'total_yards': 0,
                    'total_points': 0,
                    'avg_yards': 0,
                    'success_rate': 0,
                    'scoring_rate': 0
                }
        
        return result
    
    def _is_successful_play(self, play: Dict[str, Any]) -> bool:
        """Determine if a play was successful based on down and distance"""
        down = play.get('down')
        distance = play.get('distance', 0)
        yards_gained = play.get('yards_gained', 0)
        
        if not down or down not in self.SUCCESS_THRESHOLDS:
            # For special teams or unknown situations, use yards gained > 0
            return yards_gained > 0
        
        success_threshold = distance * self.SUCCESS_THRESHOLDS[down]
        return yards_gained >= success_threshold
    
    def compare_datasets(self, 
                        data1: Dict[str, Any], 
                        data2: Dict[str, Any],
                        labels: Tuple[str, str] = ("Team", "Opponent")) -> Dict[str, Any]:
        """
        Compare two processed datasets
        
        Args:
            data1: First dataset (processed)
            data2: Second dataset (processed) 
            labels: Labels for comparison
            
        Returns:
            Comparison analysis
        """
        comparison = {
            'summary_comparison': {},
            'formation_comparison': {},
            'play_type_comparison': {},
            'advantage_analysis': {}
        }
        
        # Summary comparison
        summary1 = data1.get('summary')
        summary2 = data2.get('summary')
        
        if summary1 and summary2:
            comparison['summary_comparison'] = {
                labels[0]: {
                    'avg_yards_per_play': summary1.avg_yards_per_play,
                    'success_rate': summary1.success_rate,
                    'explosive_plays': summary1.explosive_plays
                },
                labels[1]: {
                    'avg_yards_per_play': summary2.avg_yards_per_play,
                    'success_rate': summary2.success_rate,
                    'explosive_plays': summary2.explosive_plays
                },
                'differences': {
                    'yards_per_play_diff': summary1.avg_yards_per_play - summary2.avg_yards_per_play,
                    'success_rate_diff': summary1.success_rate - summary2.success_rate,
                    'explosive_plays_diff': summary1.explosive_plays - summary2.explosive_plays
                }
            }
        
        # Identify advantages
        advantages = []
        if summary1 and summary2:
            if summary1.avg_yards_per_play > summary2.avg_yards_per_play:
                advantages.append(f"{labels[0]} has better yards per play efficiency")
            if summary1.success_rate > summary2.success_rate:
                advantages.append(f"{labels[0]} has higher success rate")
            if summary1.explosive_plays > summary2.explosive_plays:
                advantages.append(f"{labels[0]} has more explosive plays")
        
        comparison['advantage_analysis'] = advantages
        
        return comparison


class EfficiencyCalculator:
    """
    Calculate advanced efficiency metrics for football performance
    """
    
    @staticmethod
    def calculate_epa(plays: List[Dict[str, Any]]) -> float:
        """
        Calculate Expected Points Added (simplified version)
        
        Args:
            plays: List of play data
            
        Returns:
            Average EPA per play
        """
        # Simplified EPA calculation based on field position and outcomes
        total_epa = 0
        valid_plays = 0
        
        for play in plays:
            yard_line = play.get('yard_line', 50)
            yards_gained = play.get('yards_gained', 0)
            points_scored = play.get('points_scored', 0)
            
            # Simplified expected points based on field position
            starting_ep = EfficiencyCalculator._field_position_to_ep(yard_line)
            ending_ep = EfficiencyCalculator._field_position_to_ep(yard_line + yards_gained)
            
            play_epa = (ending_ep - starting_ep) + points_scored
            total_epa += play_epa
            valid_plays += 1
        
        return total_epa / valid_plays if valid_plays > 0 else 0.0
    
    @staticmethod
    def _field_position_to_ep(yard_line: int) -> float:
        """Convert field position to expected points (simplified)"""
        # Simplified linear model: closer to goal = more expected points
        if yard_line >= 95:
            return 6.0  # Goal line = ~6 points
        elif yard_line >= 80:
            return 3.0 + (yard_line - 80) / 15 * 3  # Red zone
        elif yard_line >= 50:
            return 1.0 + (yard_line - 50) / 30 * 2  # Plus territory
        else:
            return 0.5 * (yard_line / 50)  # Minus territory
    
    @staticmethod
    def calculate_win_probability_impact(plays: List[Dict[str, Any]], 
                                       current_score_diff: int = 0) -> Dict[str, float]:
        """
        Calculate how plays impact win probability (simplified)
        
        Args:
            plays: List of play data
            current_score_diff: Current score differential
            
        Returns:
            Win probability metrics
        """
        # Simplified calculation based on points and field position
        total_points = sum(play.get('points_scored', 0) for play in plays)
        avg_field_position = np.mean([play.get('yard_line', 50) for play in plays])
        
        # Base win probability from score differential
        base_wp = 50 + (current_score_diff * 2)  # Simplified
        
        # Adjust for performance
        performance_adjustment = (total_points * 5) + ((avg_field_position - 50) * 0.2)
        
        adjusted_wp = max(0, min(100, base_wp + performance_adjustment))
        
        return {
            'base_win_probability': base_wp,
            'performance_adjusted_wp': adjusted_wp,
            'wp_added': performance_adjustment
        }
    
    @staticmethod
    def calculate_efficiency_ratings(processed_data: Dict[str, Any]) -> EfficiencyMetrics:
        """
        Calculate comprehensive efficiency ratings
        
        Args:
            processed_data: Processed play data
            
        Returns:
            EfficiencyMetrics object
        """
        situational = processed_data.get('situational', {})
        summary = processed_data.get('summary')
        
        # Overall efficiency (success rate weighted by yards)
        overall_eff = summary.success_rate if summary else 0
        
        # Situational efficiencies
        red_zone_eff = situational.get('red_zone', {}).get('success_rate', 0)
        third_down_eff = situational.get('third_down', {}).get('success_rate', 0)
        goal_line_eff = situational.get('goal_line', {}).get('success_rate', 0)
        
        # Two-minute efficiency (would need time-based data)
        two_minute_eff = 0  # Placeholder
        
        return EfficiencyMetrics(
            overall_efficiency=overall_eff,
            red_zone_efficiency=red_zone_eff,
            third_down_efficiency=third_down_eff,
            goal_line_efficiency=goal_line_eff,
            two_minute_efficiency=two_minute_eff
        )