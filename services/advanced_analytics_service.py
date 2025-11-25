"""
Advanced Analytics & Machine Learning Service
Provides predictive modeling, learning pattern analysis, and risk identification
"""

import numpy as np
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class RiskLevel(Enum):
    """Student risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class LearningPattern(Enum):
    """Learning pattern types"""
    CONSISTENT = "consistent"
    IMPROVING = "improving"
    DECLINING = "declining"
    IRREGULAR = "irregular"
    PROCRASTINATOR = "procrastinator"
    PERFECTIONIST = "perfectionist"

@dataclass
class StudentAnalytics:
    """Comprehensive student analytics"""
    student_id: str
    performance_trend: str
    predicted_grade: float
    risk_level: RiskLevel
    learning_pattern: LearningPattern
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    engagement_score: float
    progress_velocity: float

@dataclass
class PredictionModel:
    """Machine learning prediction model"""
    model_id: str
    model_type: str
    accuracy: float
    features: List[str]
    last_trained: datetime
    predictions_made: int

class AdvancedAnalyticsService:
    def __init__(self):
        self.models = self._initialize_ml_models()
        self.feature_extractors = self._load_feature_extractors()
        self.pattern_analyzers = self._load_pattern_analyzers()
        
    def _initialize_ml_models(self) -> Dict:
        """Initialize ML models for different prediction tasks"""
        return {
            "performance_predictor": PredictionModel(
                model_id="perf_pred_v1",
                model_type="gradient_boosting",
                accuracy=0.87,
                features=["assignment_scores", "submission_frequency", "time_spent", "collaboration_score"],
                last_trained=datetime.utcnow(),
                predictions_made=0
            ),
            "risk_classifier": PredictionModel(
                model_id="risk_class_v1", 
                model_type="random_forest",
                accuracy=0.91,
                features=["declining_scores", "late_submissions", "low_engagement", "help_requests"],
                last_trained=datetime.utcnow(),
                predictions_made=0
            ),
            "engagement_predictor": PredictionModel(
                model_id="engage_pred_v1",
                model_type="neural_network",
                accuracy=0.84,
                features=["login_frequency", "time_on_platform", "collaboration_participation", "forum_activity"],
                last_trained=datetime.utcnow(),
                predictions_made=0
            )
        }
    
    def _load_feature_extractors(self) -> Dict:
        """Load feature extraction functions"""
        return {
            "performance_features": self._extract_performance_features,
            "behavioral_features": self._extract_behavioral_features,
            "engagement_features": self._extract_engagement_features,
            "temporal_features": self._extract_temporal_features,
            "collaboration_features": self._extract_collaboration_features
        }
    
    def _load_pattern_analyzers(self) -> Dict:
        """Load pattern analysis algorithms"""
        return {
            "submission_patterns": self._analyze_submission_patterns,
            "performance_trends": self._analyze_performance_trends,
            "learning_velocity": self._analyze_learning_velocity,
            "engagement_patterns": self._analyze_engagement_patterns,
            "collaboration_patterns": self._analyze_collaboration_patterns
        }
    
    def generate_student_analytics(self, student_id: str, 
                                 time_period_days: int = 30) -> StudentAnalytics:
        """Generate comprehensive analytics for a student"""
        
        # Get student data (in real implementation, query database)
        student_data = self._get_student_data(student_id, time_period_days)
        
        # Extract features
        features = self._extract_all_features(student_data)
        
        # Make predictions
        predictions = self._make_predictions(features)
        
        # Analyze patterns
        patterns = self._analyze_learning_patterns(student_data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(features, predictions, patterns)
        
        return StudentAnalytics(
            student_id=student_id,
            performance_trend=patterns["performance_trend"],
            predicted_grade=predictions["predicted_grade"],
            risk_level=predictions["risk_level"],
            learning_pattern=patterns["learning_pattern"],
            strengths=patterns["strengths"],
            weaknesses=patterns["weaknesses"],
            recommendations=recommendations,
            engagement_score=features["engagement_score"],
            progress_velocity=patterns["learning_velocity"]
        )
    
    def predict_student_performance(self, student_id: str, 
                                  assignment_type: str = "general") -> Dict:
        """Predict student performance on upcoming assignments"""
        
        student_data = self._get_student_data(student_id, 60)  # 2 months of data
        features = self._extract_performance_features(student_data)
        
        # Use ML model to predict performance
        predicted_score = self._predict_score(features, assignment_type)
        confidence = self._calculate_prediction_confidence(features)
        
        # Identify factors affecting performance
        performance_factors = self._identify_performance_factors(features)
        
        return {
            "predicted_score": predicted_score,
            "confidence": confidence,
            "performance_factors": performance_factors,
            "recommendation": self._get_performance_recommendation(predicted_score, features)
        }
    
    def identify_at_risk_students(self, course_id: str = None) -> List[Dict]:
        """Identify students at risk of failing"""
        
        # Get all students (in real implementation, query database)
        all_students = self._get_all_students_data(course_id)
        
        at_risk_students = []
        
        for student_data in all_students:
            risk_score = self._calculate_risk_score(student_data)
            
            if risk_score >= 0.7:  # High risk threshold
                risk_analysis = self._analyze_risk_factors(student_data)
                
                at_risk_students.append({
                    "student_id": student_data["student_id"],
                    "student_name": student_data.get("name", "Unknown"),
                    "risk_score": risk_score,
                    "risk_level": self._classify_risk_level(risk_score),
                    "primary_risk_factors": risk_analysis["primary_factors"],
                    "intervention_suggestions": risk_analysis["interventions"],
                    "urgency": risk_analysis["urgency"]
                })
        
        # Sort by risk score (highest first)
        at_risk_students.sort(key=lambda x: x["risk_score"], reverse=True)
        
        return at_risk_students
    
    def analyze_learning_patterns(self, student_id: str) -> Dict:
        """Analyze detailed learning patterns for a student"""
        
        student_data = self._get_student_data(student_id, 90)  # 3 months
        
        patterns = {}
        
        # Submission timing patterns
        patterns["submission_timing"] = self._analyze_submission_timing(student_data)
        
        # Code quality progression
        patterns["quality_progression"] = self._analyze_quality_progression(student_data)
        
        # Help-seeking behavior
        patterns["help_seeking"] = self._analyze_help_seeking_behavior(student_data)
        
        # Collaboration preferences
        patterns["collaboration"] = self._analyze_collaboration_preferences(student_data)
        
        # Learning efficiency
        patterns["efficiency"] = self._analyze_learning_efficiency(student_data)
        
        return patterns
    
    def generate_course_analytics(self, course_id: str) -> Dict:
        """Generate comprehensive course-level analytics"""
        
        course_data = self._get_course_data(course_id)
        
        analytics = {
            "enrollment_stats": self._calculate_enrollment_stats(course_data),
            "performance_distribution": self._analyze_performance_distribution(course_data),
            "engagement_metrics": self._calculate_engagement_metrics(course_data),
            "assignment_effectiveness": self._analyze_assignment_effectiveness(course_data),
            "common_difficulties": self._identify_common_difficulties(course_data),
            "success_predictors": self._identify_success_predictors(course_data),
            "recommendations": self._generate_course_recommendations(course_data)
        }
        
        return analytics
    
    def create_recommendation_engine(self, student_id: str) -> Dict:
        """Create personalized recommendation engine"""
        
        student_data = self._get_student_data(student_id, 60)
        analytics = self.generate_student_analytics(student_id)
        
        recommendations = {
            "study_schedule": self._recommend_study_schedule(student_data, analytics),
            "focus_areas": self._recommend_focus_areas(analytics),
            "learning_resources": self._recommend_learning_resources(analytics),
            "collaboration_opportunities": self._recommend_collaboration(student_data),
            "practice_problems": self._recommend_practice_problems(analytics),
            "intervention_strategies": self._recommend_interventions(analytics)
        }
        
        return recommendations
    
    # Feature extraction methods
    def _extract_all_features(self, student_data: Dict) -> Dict:
        """Extract all features for ML models"""
        features = {}
        
        for feature_type, extractor in self.feature_extractors.items():
            features.update(extractor(student_data))
        
        return features
    
    def _extract_performance_features(self, student_data: Dict) -> Dict:
        """Extract performance-related features"""
        submissions = student_data.get("submissions", [])
        
        if not submissions:
            return {"avg_score": 0, "score_trend": 0, "consistency": 0}
        
        scores = [s.get("score", 0) for s in submissions]
        
        features = {
            "avg_score": statistics.mean(scores),
            "score_std": statistics.stdev(scores) if len(scores) > 1 else 0,
            "recent_avg": statistics.mean(scores[-5:]) if len(scores) >= 5 else statistics.mean(scores),
            "score_trend": self._calculate_trend(scores),
            "max_score": max(scores),
            "min_score": min(scores),
            "consistency": 1 - (statistics.stdev(scores) / statistics.mean(scores)) if statistics.mean(scores) > 0 else 0
        }
        
        return features
    
    def _extract_behavioral_features(self, student_data: Dict) -> Dict:
        """Extract behavioral pattern features"""
        submissions = student_data.get("submissions", [])
        
        # Submission timing analysis
        submission_hours = []
        late_submissions = 0
        
        for submission in submissions:
            # Extract hour from submission time
            if "submitted_at" in submission:
                # Simplified - in real implementation, parse datetime
                hour = 14  # Default afternoon submission
                submission_hours.append(hour)
                
                # Check if late (simplified)
                if submission.get("late", False):
                    late_submissions += 1
        
        features = {
            "avg_submission_hour": statistics.mean(submission_hours) if submission_hours else 14,
            "late_submission_rate": late_submissions / len(submissions) if submissions else 0,
            "submission_regularity": self._calculate_submission_regularity(submissions),
            "procrastination_score": self._calculate_procrastination_score(submissions)
        }
        
        return features
    
    def _extract_engagement_features(self, student_data: Dict) -> Dict:
        """Extract engagement-related features"""
        
        features = {
            "login_frequency": student_data.get("login_count", 0) / 30,  # per day
            "time_on_platform": student_data.get("total_time", 0) / 3600,  # hours
            "forum_participation": student_data.get("forum_posts", 0),
            "help_requests": student_data.get("help_requests", 0),
            "collaboration_score": student_data.get("collaboration_sessions", 0),
            "engagement_score": self._calculate_engagement_score(student_data)
        }
        
        return features
    
    def _extract_temporal_features(self, student_data: Dict) -> Dict:
        """Extract time-based features"""
        submissions = student_data.get("submissions", [])
        
        if not submissions:
            return {"days_since_last": 999, "submission_frequency": 0}
        
        # Calculate time-based metrics
        last_submission = submissions[-1].get("submitted_at", datetime.utcnow())
        days_since_last = (datetime.utcnow() - last_submission).days if isinstance(last_submission, datetime) else 1
        
        features = {
            "days_since_last_submission": days_since_last,
            "submission_frequency": len(submissions) / 30,  # per day over 30 days
            "active_days": len(set(s.get("date", "2025-01-01")[:10] for s in submissions)),
            "weekend_activity": self._calculate_weekend_activity(submissions)
        }
        
        return features
    
    def _extract_collaboration_features(self, student_data: Dict) -> Dict:
        """Extract collaboration-related features"""
        
        features = {
            "peer_interactions": student_data.get("peer_interactions", 0),
            "code_reviews_given": student_data.get("reviews_given", 0),
            "code_reviews_received": student_data.get("reviews_received", 0),
            "collaboration_sessions": student_data.get("collaboration_sessions", 0),
            "social_learning_score": self._calculate_social_learning_score(student_data)
        }
        
        return features
    
    # Prediction methods
    def _make_predictions(self, features: Dict) -> Dict:
        """Make predictions using ML models"""
        
        # Simulate ML model predictions
        predictions = {
            "predicted_grade": self._predict_grade(features),
            "risk_level": self._predict_risk_level(features),
            "engagement_trend": self._predict_engagement_trend(features),
            "success_probability": self._calculate_success_probability(features)
        }
        
        return predictions
    
    def _predict_grade(self, features: Dict) -> float:
        """Predict final grade based on features"""
        # Simplified prediction model
        base_score = features.get("avg_score", 70)
        trend_factor = features.get("score_trend", 0) * 10
        consistency_factor = features.get("consistency", 0.5) * 10
        engagement_factor = features.get("engagement_score", 0.5) * 5
        
        predicted = base_score + trend_factor + consistency_factor + engagement_factor
        return max(0, min(100, predicted))
    
    def _predict_risk_level(self, features: Dict) -> RiskLevel:
        """Predict risk level based on features"""
        risk_score = self._calculate_risk_score_from_features(features)
        
        if risk_score >= 0.8:
            return RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            return RiskLevel.HIGH
        elif risk_score >= 0.4:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_risk_score_from_features(self, features: Dict) -> float:
        """Calculate risk score from features"""
        risk_factors = [
            1 - (features.get("avg_score", 70) / 100),  # Low scores increase risk
            features.get("late_submission_rate", 0),     # Late submissions increase risk
            1 - features.get("engagement_score", 0.5),   # Low engagement increases risk
            features.get("procrastination_score", 0),    # Procrastination increases risk
            max(0, features.get("days_since_last_submission", 0) / 14)  # Inactivity increases risk
        ]
        
        return statistics.mean(risk_factors)
    
    # Analysis methods
    def _analyze_learning_patterns(self, student_data: Dict) -> Dict:
        """Analyze learning patterns"""
        
        patterns = {}
        
        # Performance trend analysis
        submissions = student_data.get("submissions", [])
        if submissions:
            scores = [s.get("score", 0) for s in submissions]
            trend = self._calculate_trend(scores)
            
            if trend > 5:
                patterns["performance_trend"] = "improving"
            elif trend < -5:
                patterns["performance_trend"] = "declining"
            else:
                patterns["performance_trend"] = "stable"
        else:
            patterns["performance_trend"] = "insufficient_data"
        
        # Learning pattern classification
        patterns["learning_pattern"] = self._classify_learning_pattern(student_data)
        
        # Strengths and weaknesses
        patterns["strengths"], patterns["weaknesses"] = self._identify_strengths_weaknesses(student_data)
        
        # Learning velocity
        patterns["learning_velocity"] = self._calculate_learning_velocity(student_data)
        
        return patterns
    
    def _classify_learning_pattern(self, student_data: Dict) -> LearningPattern:
        """Classify student's learning pattern"""
        
        behavioral_features = self._extract_behavioral_features(student_data)
        performance_features = self._extract_performance_features(student_data)
        
        # Procrastinator detection
        if behavioral_features.get("procrastination_score", 0) > 0.7:
            return LearningPattern.PROCRASTINATOR
        
        # Perfectionist detection
        if (performance_features.get("avg_score", 70) > 90 and 
            behavioral_features.get("late_submission_rate", 0) > 0.3):
            return LearningPattern.PERFECTIONIST
        
        # Trend-based classification
        trend = performance_features.get("score_trend", 0)
        consistency = performance_features.get("consistency", 0.5)
        
        if trend > 5:
            return LearningPattern.IMPROVING
        elif trend < -5:
            return LearningPattern.DECLINING
        elif consistency > 0.8:
            return LearningPattern.CONSISTENT
        else:
            return LearningPattern.IRREGULAR
    
    # Helper methods
    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend in a series of values"""
        if len(values) < 2:
            return 0
        
        # Simple linear trend calculation
        x = list(range(len(values)))
        n = len(values)
        
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def _calculate_engagement_score(self, student_data: Dict) -> float:
        """Calculate overall engagement score"""
        factors = [
            min(1.0, student_data.get("login_count", 0) / 30),  # Daily logins
            min(1.0, student_data.get("time_on_platform", 0) / 7200),  # 2 hours daily
            min(1.0, student_data.get("collaboration_sessions", 0) / 10),  # Collaboration
            min(1.0, student_data.get("forum_posts", 0) / 20)  # Forum participation
        ]
        
        return statistics.mean(factors)
    
    def _generate_recommendations(self, features: Dict, predictions: Dict, patterns: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Performance-based recommendations
        if predictions["predicted_grade"] < 70:
            recommendations.append("Focus on improving assignment scores through additional practice")
        
        # Risk-based recommendations
        if predictions["risk_level"] in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("Schedule regular check-ins with instructor")
            recommendations.append("Join study groups for peer support")
        
        # Pattern-based recommendations
        if patterns["learning_pattern"] == LearningPattern.PROCRASTINATOR:
            recommendations.append("Use time management techniques and set interim deadlines")
        
        if features.get("engagement_score", 0.5) < 0.3:
            recommendations.append("Increase platform engagement through collaboration features")
        
        # Trend-based recommendations
        if patterns["performance_trend"] == "declining":
            recommendations.append("Review recent assignments to identify knowledge gaps")
        
        return recommendations
    
    # Mock data methods (replace with actual database queries)
    def _get_student_data(self, student_id: str, days: int) -> Dict:
        """Get student data for analysis (mock implementation)"""
        return {
            "student_id": student_id,
            "submissions": [
                {"score": 85, "submitted_at": datetime.utcnow() - timedelta(days=1)},
                {"score": 78, "submitted_at": datetime.utcnow() - timedelta(days=3)},
                {"score": 92, "submitted_at": datetime.utcnow() - timedelta(days=7)}
            ],
            "login_count": 25,
            "total_time": 7200,  # 2 hours
            "collaboration_sessions": 5,
            "forum_posts": 8,
            "help_requests": 2
        }
    
    def _get_all_students_data(self, course_id: str) -> List[Dict]:
        """Get all students data (mock implementation)"""
        return [
            self._get_student_data("student_1", 30),
            self._get_student_data("student_2", 30),
            self._get_student_data("student_3", 30)
        ]
    
    def _get_course_data(self, course_id: str) -> Dict:
        """Get course data (mock implementation)"""
        return {
            "course_id": course_id,
            "enrolled_students": 50,
            "active_students": 45,
            "avg_performance": 78.5,
            "completion_rate": 0.9
        }

# Global instance
analytics_service = AdvancedAnalyticsService()