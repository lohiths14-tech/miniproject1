"""
Gamification Service - Points, Badges, Streaks, and Achievements System
Provides comprehensive engagement features to enhance student learning experience
"""

from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional
from enum import Enum

class BadgeType(Enum):
    """Badge categories for different achievements"""
    STREAK = "streak"
    ACCURACY = "accuracy"
    SPEED = "speed"
    COLLABORATION = "collaboration"
    IMPROVEMENT = "improvement"
    MILESTONE = "milestone"
    LANGUAGE = "language"
    CHALLENGE = "challenge"

class AchievementLevel(Enum):
    """Achievement difficulty levels"""
    BRONZE = "bronze"
    SILVER = "silver"
    GOLD = "gold"
    PLATINUM = "platinum"
    DIAMOND = "diamond"

class GamificationService:
    def __init__(self):
        self.achievements_config = self._load_achievements_config()
        self.point_values = self._load_point_values()
    
    def _load_achievements_config(self) -> Dict:
        """Load achievement definitions and badge requirements"""
        return {
            "badges": {
                "first_submission": {
                    "name": "First Steps",
                    "description": "Submitted your first assignment",
                    "type": BadgeType.MILESTONE.value,
                    "level": AchievementLevel.BRONZE.value,
                    "points": 50,
                    "icon": "🎯"
                },
                "streak_3": {
                    "name": "On Fire",
                    "description": "3-day submission streak",
                    "type": BadgeType.STREAK.value,
                    "level": AchievementLevel.BRONZE.value,
                    "points": 100,
                    "icon": "🔥"
                },
                "streak_7": {
                    "name": "Week Warrior",
                    "description": "7-day submission streak",
                    "type": BadgeType.STREAK.value,
                    "level": AchievementLevel.SILVER.value,
                    "points": 250,
                    "icon": "🏆"
                },
                "streak_30": {
                    "name": "Coding Legend",
                    "description": "30-day submission streak",
                    "type": BadgeType.STREAK.value,
                    "level": AchievementLevel.GOLD.value,
                    "points": 1000,
                    "icon": "👑"
                },
                "perfect_score": {
                    "name": "Perfectionist",
                    "description": "Achieved 100% score on an assignment",
                    "type": BadgeType.ACCURACY.value,
                    "level": AchievementLevel.SILVER.value,
                    "points": 200,
                    "icon": "💯"
                },
                "speed_demon": {
                    "name": "Speed Demon",
                    "description": "Completed assignment in under 5 minutes",
                    "type": BadgeType.SPEED.value,
                    "level": AchievementLevel.GOLD.value,
                    "points": 300,
                    "icon": "⚡"
                },
                "multi_language": {
                    "name": "Polyglot",
                    "description": "Submitted in 3+ programming languages",
                    "type": BadgeType.LANGUAGE.value,
                    "level": AchievementLevel.SILVER.value,
                    "points": 400,
                    "icon": "🌍"
                },
                "first_place": {
                    "name": "Champion",
                    "description": "Ranked #1 on leaderboard",
                    "type": BadgeType.MILESTONE.value,
                    "level": AchievementLevel.PLATINUM.value,
                    "points": 500,
                    "icon": "🥇"
                },
                "improver": {
                    "name": "Rising Star",
                    "description": "Improved score by 30+ points",
                    "type": BadgeType.IMPROVEMENT.value,
                    "level": AchievementLevel.BRONZE.value,
                    "points": 150,
                    "icon": "📈"
                },
                "helper": {
                    "name": "Team Player",
                    "description": "Participated in 5+ collaboration sessions",
                    "type": BadgeType.COLLABORATION.value,
                    "level": AchievementLevel.SILVER.value,
                    "points": 250,
                    "icon": "🤝"
                }
            },
            "challenges": {
                "monthly_python": {
                    "name": "Python Master",
                    "description": "Complete 10 Python assignments this month",
                    "type": BadgeType.CHALLENGE.value,
                    "level": AchievementLevel.GOLD.value,
                    "points": 750,
                    "icon": "🐍",
                    "deadline": "monthly",
                    "requirement": {"language": "python", "count": 10}
                },
                "efficiency_guru": {
                    "name": "Efficiency Guru",
                    "description": "Achieve optimal time complexity in 5 assignments",
                    "type": BadgeType.CHALLENGE.value,
                    "level": AchievementLevel.PLATINUM.value,
                    "points": 1000,
                    "icon": "⚙️",
                    "deadline": "monthly",
                    "requirement": {"optimal_complexity": 5}
                }
            }
        }
    
    def _load_point_values(self) -> Dict:
        """Define point values for different actions"""
        return {
            "submission": 10,
            "correct_test_case": 5,
            "perfect_score": 50,
            "first_attempt_success": 25,
            "improvement": 15,
            "streak_bonus": 10,  # per day in streak
            "collaboration_session": 20,
            "help_peer": 30,
            "daily_login": 5,
            "assignment_completion": 100
        }
    
    def calculate_points(self, user_id: str, action: str, metadata: Dict = None) -> int:
        """Calculate points earned for a specific action"""
        metadata = metadata or {}
        base_points = self.point_values.get(action, 0)
        
        # Apply multipliers based on metadata
        multiplier = 1.0
        
        if action == "submission":
            score = metadata.get("score", 0)
            multiplier = 1 + (score / 100)  # Bonus for higher scores
            
        elif action == "streak_bonus":
            streak_days = metadata.get("streak_days", 1)
            multiplier = min(3.0, 1 + (streak_days * 0.1))  # Max 3x multiplier
            
        elif action == "improvement":
            improvement_percent = metadata.get("improvement_percent", 0)
            multiplier = 1 + (improvement_percent / 100)
        
        return int(base_points * multiplier)
    
    def check_badge_eligibility(self, user_stats: Dict) -> List[Dict]:
        """Check which new badges a user has earned"""
        earned_badges = []
        current_badges = set(user_stats.get("badges", []))
        
        for badge_id, badge_config in self.achievements_config["badges"].items():
            if badge_id in current_badges:
                continue
                
            if self._meets_badge_requirements(badge_id, badge_config, user_stats):
                earned_badges.append({
                    "badge_id": badge_id,
                    "config": badge_config,
                    "earned_at": datetime.utcnow().isoformat()
                })
        
        return earned_badges
    
    def _meets_badge_requirements(self, badge_id: str, badge_config: Dict, user_stats: Dict) -> bool:
        """Check if user meets specific badge requirements"""
        badge_type = badge_config["type"]
        
        if badge_id == "first_submission":
            return user_stats.get("total_submissions", 0) >= 1
            
        elif badge_id.startswith("streak_"):
            required_streak = int(badge_id.split("_")[1])
            return user_stats.get("current_streak", 0) >= required_streak
            
        elif badge_id == "perfect_score":
            return user_stats.get("perfect_scores", 0) >= 1
            
        elif badge_id == "speed_demon":
            fastest_time = user_stats.get("fastest_completion", float('inf'))
            return fastest_time <= 300  # 5 minutes
            
        elif badge_id == "multi_language":
            languages_used = len(user_stats.get("languages_used", []))
            return languages_used >= 3
            
        elif badge_id == "first_place":
            return user_stats.get("leaderboard_rank", float('inf')) == 1
            
        elif badge_id == "improver":
            return user_stats.get("max_improvement", 0) >= 30
            
        elif badge_id == "helper":
            return user_stats.get("collaboration_sessions", 0) >= 5
        
        return False
    
    def update_streak(self, user_id: str, last_submission_date: datetime) -> Dict:
        """Update user's submission streak"""
        today = datetime.utcnow().date()
        last_date = last_submission_date.date() if last_submission_date else None
        
        if not last_date:
            return {"current_streak": 1, "longest_streak": 1, "streak_broken": False}
        
        days_diff = (today - last_date).days
        
        # Load current streak data (would come from database)
        current_streak = 1  # This would be loaded from user stats
        longest_streak = 1  # This would be loaded from user stats
        
        if days_diff == 0:
            # Same day submission, don't change streak
            return {"current_streak": current_streak, "longest_streak": longest_streak, "streak_broken": False}
        elif days_diff == 1:
            # Consecutive day, increment streak
            current_streak += 1
            longest_streak = max(longest_streak, current_streak)
            return {"current_streak": current_streak, "longest_streak": longest_streak, "streak_broken": False}
        else:
            # Streak broken, reset to 1
            return {"current_streak": 1, "longest_streak": longest_streak, "streak_broken": True}
    
    def get_leaderboard(self, course_id: str = None, timeframe: str = "all") -> List[Dict]:
        """Generate leaderboard based on points and achievements"""
        # This would query the database for user stats
        # Placeholder implementation
        leaderboard = []
        
        # Example leaderboard structure
        sample_users = [
            {
                "user_id": "student1",
                "username": "alice_codes",
                "total_points": 2500,
                "badges_count": 8,
                "current_streak": 15,
                "perfect_scores": 5,
                "rank": 1
            },
            {
                "user_id": "student2", 
                "username": "bob_dev",
                "total_points": 2200,
                "badges_count": 6,
                "current_streak": 8,
                "perfect_scores": 3,
                "rank": 2
            }
        ]
        
        return sample_users
    
    def get_user_achievements_summary(self, user_id: str) -> Dict:
        """Get comprehensive achievement summary for a user"""
        # This would query user's actual data from database
        return {
            "total_points": 1850,
            "rank": 3,
            "badges": [
                {
                    "badge_id": "first_submission",
                    "earned_at": "2025-09-15T10:30:00Z",
                    "config": self.achievements_config["badges"]["first_submission"]
                },
                {
                    "badge_id": "streak_7",
                    "earned_at": "2025-09-22T14:15:00Z", 
                    "config": self.achievements_config["badges"]["streak_7"]
                }
            ],
            "current_streak": 12,
            "longest_streak": 15,
            "next_badges": [
                {
                    "badge_id": "streak_30",
                    "progress": 12,
                    "required": 30,
                    "config": self.achievements_config["badges"]["streak_30"]
                },
                {
                    "badge_id": "perfect_score",
                    "progress": 0,
                    "required": 1,
                    "config": self.achievements_config["badges"]["perfect_score"]
                }
            ],
            "recent_activities": [
                {
                    "type": "points_earned",
                    "amount": 85,
                    "reason": "Assignment submission with 95% score",
                    "timestamp": "2025-09-27T09:00:00Z"
                },
                {
                    "type": "badge_earned",
                    "badge": "streak_7",
                    "timestamp": "2025-09-22T14:15:00Z"
                }
            ]
        }
    
    def calculate_level_from_points(self, total_points: int) -> Dict:
        """Calculate user level based on total points"""
        level_thresholds = [
            (0, "Beginner", "🌱"),
            (500, "Novice", "🌿"),
            (1500, "Intermediate", "🌳"),
            (3000, "Advanced", "🚀"),
            (6000, "Expert", "⭐"),
            (12000, "Master", "💎"),
            (25000, "Legend", "👑")
        ]
        
        current_level = level_thresholds[0]
        next_level = None
        
        for i, (threshold, name, icon) in enumerate(level_thresholds):
            if total_points >= threshold:
                current_level = (threshold, name, icon)
                next_level = level_thresholds[i + 1] if i + 1 < len(level_thresholds) else None
            else:
                break
        
        progress = 0
        if next_level:
            current_threshold = current_level[0]
            next_threshold = next_level[0]
            progress = ((total_points - current_threshold) / (next_threshold - current_threshold)) * 100
        
        return {
            "current_level": {
                "threshold": current_level[0],
                "name": current_level[1],
                "icon": current_level[2]
            },
            "next_level": {
                "threshold": next_level[0] if next_level else None,
                "name": next_level[1] if next_level else None,
                "icon": next_level[2] if next_level else None
            } if next_level else None,
            "progress_percent": min(100, progress),
            "points_to_next": (next_level[0] - total_points) if next_level else 0
        }
    
    def get_monthly_challenges(self) -> List[Dict]:
        """Get current monthly challenges"""
        challenges = []
        current_month = datetime.utcnow().strftime("%Y-%m")
        
        for challenge_id, challenge_config in self.achievements_config["challenges"].items():
            if challenge_config["deadline"] == "monthly":
                challenges.append({
                    "challenge_id": challenge_id,
                    "config": challenge_config,
                    "deadline": f"{current_month}-30T23:59:59Z",
                    "participation_count": 0  # Would be calculated from database
                })
        
        return challenges
    
    def award_points_and_badges(self, user_id: str, action: str, metadata: Dict = None) -> Dict:
        """Main method to award points and check for new badges"""
        # Calculate points earned
        points_earned = self.calculate_points(user_id, action, metadata)
        
        # This would update the database with new points
        # For now, we'll return the calculation result
        
        # Check for new badges (would require current user stats from database)
        user_stats = {}  # Would be loaded from database
        new_badges = self.check_badge_eligibility(user_stats)
        
        return {
            "points_earned": points_earned,
            "new_badges": new_badges,
            "action": action,
            "timestamp": datetime.utcnow().isoformat()
        }

# Global instance
gamification_service = GamificationService()