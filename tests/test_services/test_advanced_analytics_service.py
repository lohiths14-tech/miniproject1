"""Tests for Advanced Analytics Service."""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from services.advanced_analytics_service import (
    AdvancedAnalyticsService,
    RiskLevel,
    LearningPattern,
    StudentAnalytics,
)


class TestAdvancedAnalyticsService:
    """Test suite for AdvancedAnalyticsService."""

    @pytest.fixture
    def analytics_service(self):
        """Create an instance of AdvancedAnalyticsService."""
        return AdvancedAnalyticsService()

    @pytest.fixture
    def sample_student_data(self):
        """Sample student data for testing."""
        return {
            "student_id": "student_123",
            "submissions": [
                {"score": 85, "submitted_at": datetime.utcnow() - timedelta(days=1)},
                {"score": 78, "submitted_at": datetime.utcnow() - timedelta(days=3)},
                {"score": 92, "submitted_at": datetime.utcnow() - timedelta(days=7)},
            ],
            "login_count": 25,
            "total_time": 7200,
            "collaboration_sessions": 5,
            "forum_posts": 8,
            "help_requests": 2,
        }


class TestGenerateStudentAnalytics:
    """Tests for generate_student_analytics method."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    def test_generate_student_analytics_returns_student_analytics(self, analytics_service):
        """Test that generate_student_analytics returns a StudentAnalytics object."""
        result = analytics_service.generate_student_analytics("student_123")

        assert isinstance(result, StudentAnalytics)
        assert result.student_id == "student_123"

    def test_generate_student_analytics_has_required_fields(self, analytics_service):
        """Test that StudentAnalytics has all required fields."""
        result = analytics_service.generate_student_analytics("student_123")

        assert hasattr(result, "performance_trend")
        assert hasattr(result, "predicted_grade")
        assert hasattr(result, "risk_level")
        assert hasattr(result, "learning_pattern")
        assert hasattr(result, "strengths")
        assert hasattr(result, "weaknesses")
        assert hasattr(result, "recommendations")
        assert hasattr(result, "engagement_score")
        assert hasattr(result, "progress_velocity")

    def test_predicted_grade_in_valid_range(self, analytics_service):
        """Test that predicted grade is within 0-100 range."""
        result = analytics_service.generate_student_analytics("student_123")

        assert 0 <= result.predicted_grade <= 100

    def test_risk_level_is_valid_enum(self, analytics_service):
        """Test that risk level is a valid RiskLevel enum."""
        result = analytics_service.generate_student_analytics("student_123")

        assert isinstance(result.risk_level, RiskLevel)

    def test_learning_pattern_is_valid_enum(self, analytics_service):
        """Test that learning pattern is a valid LearningPattern enum."""
        result = analytics_service.generate_student_analytics("student_123")

        assert isinstance(result.learning_pattern, LearningPattern)


class TestPredictStudentPerformance:
    """Tests for predict_student_performance method."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    def test_predict_performance_returns_dict(self, analytics_service):
        """Test that predict_student_performance returns a dictionary."""
        result = analytics_service.predict_student_performance("student_123")

        assert isinstance(result, dict)

    def test_predict_performance_has_required_keys(self, analytics_service):
        """Test that prediction result has required keys."""
        result = analytics_service.predict_student_performance("student_123")

        assert "predicted_score" in result
        assert "confidence" in result
        assert "performance_factors" in result
        assert "recommendation" in result

    def test_predicted_score_in_valid_range(self, analytics_service):
        """Test that predicted score is within valid range."""
        result = analytics_service.predict_student_performance("student_123")

        assert 0 <= result["predicted_score"] <= 100

    def test_confidence_in_valid_range(self, analytics_service):
        """Test that confidence is between 0 and 1."""
        result = analytics_service.predict_student_performance("student_123")

        assert 0 <= result["confidence"] <= 1


class TestIdentifyAtRiskStudents:
    """Tests for identify_at_risk_students method."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    def test_identify_at_risk_returns_list(self, analytics_service):
        """Test that identify_at_risk_students returns a list."""
        result = analytics_service.identify_at_risk_students()

        assert isinstance(result, list)

    def test_at_risk_students_sorted_by_risk_score(self, analytics_service):
        """Test that at-risk students are sorted by risk score (highest first)."""
        result = analytics_service.identify_at_risk_students()

        if len(result) > 1:
            for i in range(len(result) - 1):
                assert result[i]["risk_score"] >= result[i + 1]["risk_score"]


class TestAnalyzeLearningPatterns:
    """Tests for analyze_learning_patterns method."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    def test_analyze_learning_patterns_returns_dict(self, analytics_service):
        """Test that analyze_learning_patterns returns a dictionary."""
        result = analytics_service.analyze_learning_patterns("student_123")

        assert isinstance(result, dict)

    def test_analyze_learning_patterns_has_expected_keys(self, analytics_service):
        """Test that learning patterns analysis has expected keys."""
        result = analytics_service.analyze_learning_patterns("student_123")

        assert "submission_timing" in result
        assert "quality_progression" in result
        assert "help_seeking" in result
        assert "collaboration" in result
        assert "efficiency" in result


class TestGenerateCourseAnalytics:
    """Tests for generate_course_analytics method."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    def test_generate_course_analytics_returns_dict(self, analytics_service):
        """Test that generate_course_analytics returns a dictionary."""
        result = analytics_service.generate_course_analytics("course_123")

        assert isinstance(result, dict)

    def test_course_analytics_has_required_keys(self, analytics_service):
        """Test that course analytics has required keys."""
        result = analytics_service.generate_course_analytics("course_123")

        assert "enrollment_stats" in result
        assert "performance_distribution" in result
        assert "engagement_metrics" in result
        assert "assignment_effectiveness" in result
        assert "common_difficulties" in result
        assert "success_predictors" in result
        assert "recommendations" in result


class TestFeatureExtraction:
    """Tests for feature extraction methods."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    @pytest.fixture
    def sample_student_data(self):
        return {
            "student_id": "student_123",
            "submissions": [
                {"score": 85, "submitted_at": datetime.utcnow() - timedelta(days=1)},
                {"score": 78, "submitted_at": datetime.utcnow() - timedelta(days=3)},
                {"score": 92, "submitted_at": datetime.utcnow() - timedelta(days=7)},
            ],
            "login_count": 25,
            "total_time": 7200,
            "collaboration_sessions": 5,
            "forum_posts": 8,
            "help_requests": 2,
        }

    def test_extract_performance_features(self, analytics_service, sample_student_data):
        """Test performance feature extraction."""
        features = analytics_service._extract_performance_features(sample_student_data)

        assert "avg_score" in features
        assert "score_trend" in features
        assert "consistency" in features

    def test_extract_performance_features_empty_submissions(self, analytics_service):
        """Test performance feature extraction with empty submissions."""
        student_data = {"submissions": []}
        features = analytics_service._extract_performance_features(student_data)

        assert features["avg_score"] == 0
        assert features["score_trend"] == 0
        assert features["consistency"] == 0

    def test_extract_engagement_features(self, analytics_service, sample_student_data):
        """Test engagement feature extraction."""
        features = analytics_service._extract_engagement_features(sample_student_data)

        assert "login_frequency" in features
        assert "time_on_platform" in features
        assert "engagement_score" in features

    def test_extract_behavioral_features(self, analytics_service, sample_student_data):
        """Test behavioral feature extraction."""
        features = analytics_service._extract_behavioral_features(sample_student_data)

        assert "avg_submission_hour" in features
        assert "late_submission_rate" in features
        assert "procrastination_score" in features


class TestTrendCalculation:
    """Tests for trend calculation."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    def test_calculate_trend_increasing(self, analytics_service):
        """Test trend calculation for increasing values."""
        values = [60, 70, 80, 90, 100]
        trend = analytics_service._calculate_trend(values)

        assert trend > 0

    def test_calculate_trend_decreasing(self, analytics_service):
        """Test trend calculation for decreasing values."""
        values = [100, 90, 80, 70, 60]
        trend = analytics_service._calculate_trend(values)

        assert trend < 0

    def test_calculate_trend_stable(self, analytics_service):
        """Test trend calculation for stable values."""
        values = [80, 80, 80, 80, 80]
        trend = analytics_service._calculate_trend(values)

        assert trend == 0

    def test_calculate_trend_single_value(self, analytics_service):
        """Test trend calculation with single value."""
        values = [80]
        trend = analytics_service._calculate_trend(values)

        assert trend == 0


class TestRecommendationEngine:
    """Tests for recommendation engine."""

    @pytest.fixture
    def analytics_service(self):
        return AdvancedAnalyticsService()

    def test_create_recommendation_engine_returns_dict(self, analytics_service):
        """Test that create_recommendation_engine returns a dictionary."""
        result = analytics_service.create_recommendation_engine("student_123")

        assert isinstance(result, dict)

    def test_recommendation_engine_has_required_keys(self, analytics_service):
        """Test that recommendation engine has required keys."""
        result = analytics_service.create_recommendation_engine("student_123")

        assert "study_schedule" in result
        assert "focus_areas" in result
        assert "learning_resources" in result
        assert "collaboration_opportunities" in result
        assert "practice_problems" in result
        assert "intervention_strategies" in result
