"""Tests for Progress Tracker Service.

Tests progress calculation, milestone tracking, and student analytics.
Requirements: 2.1, 2.2
"""
import pytest
from services.progress_tracker_service import ProgressTrackerService


class TestProgressTrackerServiceInit:
    """Test suite for ProgressTrackerService initialization."""

    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = ProgressTrackerService()
        assert service is not None
        assert hasattr(service, 'submissions_data')

    def test_submissions_data_loaded(self):
        """Test that submissions data is loaded on init."""
        service = ProgressTrackerService()
        # Should have loaded data (may be empty list if file not found)
        assert isinstance(service.submissions_data, list)


class TestStudentOverview:
    """Test suite for student overview functionality."""

    def test_get_student_overview_returns_dict(self):
        """Test that get_student_overview returns a dictionary."""
        service = ProgressTrackerService()
        result = service.get_student_overview("test_student")

        assert isinstance(result, dict)
        assert "overview" in result
        assert "skill_progress" in result
        assert "profile" in result

    def test_overview_contains_required_fields(self):
        """Test that overview contains all required fields."""
        service = ProgressTrackerService()
        result = service.get_student_overview("test_student")

        overview = result["overview"]
        required_fields = [
            "total_assignments",
            "average_score",
            "total_score",
            "max_possible",
            "completion_rate",
            "current_streak",
            "longest_streak",
            "recent_trend"
        ]

        for field in required_fields:
            assert field in overview, f"Missing field: {field}"

    def test_overview_for_nonexistent_student(self):
        """Test overview for a student with no submissions."""
        service = ProgressTrackerService()
        result = service.get_student_overview("nonexistent_student_xyz")

        assert result["overview"]["total_assignments"] == 0
        assert result["overview"]["average_score"] == 0
        assert result["overview"]["recent_trend"] == "no_data"

    def test_profile_contains_required_fields(self):
        """Test that profile contains required fields."""
        service = ProgressTrackerService()
        result = service.get_student_overview("test_student")

        profile = result["profile"]
        required_fields = ["student_id", "name", "email", "major", "year", "gpa"]

        for field in required_fields:
            assert field in profile, f"Missing profile field: {field}"


class TestPerformanceTimeline:
    """Test suite for performance timeline functionality."""

    def test_get_performance_timeline_returns_dict(self):
        """Test that get_performance_timeline returns a dictionary."""
        service = ProgressTrackerService()
        result = service.get_performance_timeline("test_student")

        assert isinstance(result, dict)
        assert "timeline" in result
        assert "metrics" in result

    def test_timeline_metrics_structure(self):
        """Test that timeline metrics have correct structure."""
        service = ProgressTrackerService()
        result = service.get_performance_timeline("test_student")

        metrics = result["metrics"]
        assert "score_trend" in metrics
        assert "submission_count" in metrics
        assert "labels" in metrics

        assert isinstance(metrics["score_trend"], list)
        assert isinstance(metrics["submission_count"], list)
        assert isinstance(metrics["labels"], list)

    def test_timeline_with_different_periods(self):
        """Test timeline with different time periods."""
        service = ProgressTrackerService()

        for period in ["6months", "3months", "1month"]:
            result = service.get_performance_timeline("test_student", period)
            assert isinstance(result, dict)
            assert "timeline" in result


class TestSkillAnalysis:
    """Test suite for skill analysis functionality."""

    def test_get_skill_analysis_returns_dict(self):
        """Test that get_skill_analysis returns a dictionary."""
        service = ProgressTrackerService()
        result = service.get_skill_analysis("test_student")

        assert isinstance(result, dict)
        assert "skills" in result
        assert "strongest_skills" in result
        assert "improvement_areas" in result

    def test_skill_analysis_for_nonexistent_student(self):
        """Test skill analysis for student with no data."""
        service = ProgressTrackerService()
        result = service.get_skill_analysis("nonexistent_student_xyz")

        assert result["skills"] == {}
        assert result["strongest_skills"] == []
        assert result["improvement_areas"] == []


class TestComparativeAnalysis:
    """Test suite for comparative analysis functionality."""

    def test_get_comparative_analysis_returns_dict(self):
        """Test that get_comparative_analysis returns a dictionary."""
        service = ProgressTrackerService()
        result = service.get_comparative_analysis("test_student")

        assert isinstance(result, dict)
        assert "student_average" in result
        assert "class_average" in result
        assert "percentile" in result
        assert "rank" in result
        assert "total_students" in result

    def test_comparative_analysis_contains_comparisons(self):
        """Test that comparative analysis contains comparison data."""
        service = ProgressTrackerService()
        result = service.get_comparative_analysis("test_student")

        assert "performance_comparison" in result
        assert "peer_comparison" in result

        perf_comp = result["performance_comparison"]
        assert "above_average" in perf_comp
        assert "difference" in perf_comp
        assert "percentage_difference" in perf_comp

    def test_comparative_analysis_for_nonexistent_student(self):
        """Test comparative analysis for student with no data."""
        service = ProgressTrackerService()
        result = service.get_comparative_analysis("nonexistent_student_xyz")

        assert result["student_average"] == 0
        assert result["percentile"] == 0
        assert result["rank"] == 0


class TestAchievementProgress:
    """Test suite for achievement progress functionality."""

    def test_get_achievement_progress_returns_dict(self):
        """Test that get_achievement_progress returns a dictionary."""
        service = ProgressTrackerService()
        result = service.get_achievement_progress("test_student")

        assert isinstance(result, dict)
        assert "achievements" in result
        assert "earned_count" in result
        assert "total_count" in result

    def test_achievements_have_required_fields(self):
        """Test that achievements have required fields."""
        service = ProgressTrackerService()
        result = service.get_achievement_progress("test_student")

        for achievement in result["achievements"]:
            assert "name" in achievement
            assert "description" in achievement
            assert "earned" in achievement

    def test_earned_count_matches_achievements(self):
        """Test that earned_count matches actual earned achievements."""
        service = ProgressTrackerService()
        result = service.get_achievement_progress("test_student")

        actual_earned = len([a for a in result["achievements"] if a.get("earned", False)])
        assert result["earned_count"] == actual_earned

    def test_total_count_matches_achievements(self):
        """Test that total_count matches total achievements."""
        service = ProgressTrackerService()
        result = service.get_achievement_progress("test_student")

        assert result["total_count"] == len(result["achievements"])


class TestDetailedRecommendations:
    """Test suite for detailed recommendations functionality."""

    def test_get_detailed_recommendations_returns_dict(self):
        """Test that get_detailed_recommendations returns a dictionary."""
        service = ProgressTrackerService()
        result = service.get_detailed_recommendations("test_student")

        assert isinstance(result, dict)
        assert "immediate_actions" in result
        assert "skill_development" in result
        assert "study_plan" in result
        assert "resources" in result

    def test_recommendations_have_lists(self):
        """Test that recommendations contain lists."""
        service = ProgressTrackerService()
        result = service.get_detailed_recommendations("test_student")

        assert isinstance(result["immediate_actions"], list)
        assert isinstance(result["skill_development"], list)
        assert len(result["immediate_actions"]) > 0
        assert len(result["skill_development"]) > 0

    def test_study_plan_structure(self):
        """Test that study plan has correct structure."""
        service = ProgressTrackerService()
        result = service.get_detailed_recommendations("test_student")

        study_plan = result["study_plan"]
        assert "this_week" in study_plan
        assert "this_month" in study_plan
        assert "this_semester" in study_plan

    def test_resources_have_required_fields(self):
        """Test that resources have required fields."""
        service = ProgressTrackerService()
        result = service.get_detailed_recommendations("test_student")

        for resource in result["resources"]:
            assert "type" in resource
            assert "title" in resource
            assert "url" in resource


class TestHelperMethods:
    """Test suite for helper methods."""

    def test_score_to_level_expert(self):
        """Test score to level conversion for expert."""
        service = ProgressTrackerService()
        assert service._score_to_level(95) == "Expert"
        assert service._score_to_level(90) == "Expert"

    def test_score_to_level_advanced(self):
        """Test score to level conversion for advanced."""
        service = ProgressTrackerService()
        assert service._score_to_level(85) == "Advanced"
        assert service._score_to_level(80) == "Advanced"

    def test_score_to_level_intermediate(self):
        """Test score to level conversion for intermediate."""
        service = ProgressTrackerService()
        assert service._score_to_level(75) == "Intermediate"
        assert service._score_to_level(70) == "Intermediate"

    def test_score_to_level_beginner(self):
        """Test score to level conversion for beginner."""
        service = ProgressTrackerService()
        assert service._score_to_level(65) == "Beginner"
        assert service._score_to_level(60) == "Beginner"

    def test_score_to_level_novice(self):
        """Test score to level conversion for novice."""
        service = ProgressTrackerService()
        assert service._score_to_level(50) == "Novice"
        assert service._score_to_level(0) == "Novice"
