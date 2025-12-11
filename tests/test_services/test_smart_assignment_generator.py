"""Tests for Smart Assignment Generator Service."""
import pytest
from datetime import datetime

from services.smart_assignment_generator import (
    SmartAssignmentGenerator,
    StudentProfile,
    GeneratedAssignment,
    DifficultyLevel,
    ProblemCategory,
)


class TestSmartAssignmentGenerator:
    """Test suite for SmartAssignmentGenerator."""

    @pytest.fixture
    def generator(self):
        """Create an instance of SmartAssignmentGenerator."""
        return SmartAssignmentGenerator()

    @pytest.fixture
    def sample_student_profile(self):
        """Create a sample student profile for testing."""
        return StudentProfile(
            student_id="student_123",
            skill_levels={"arrays_strings": 3, "linked_lists": 2, "dynamic_programming": 1},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=["recursion", "dynamic_programming"],
            strong_areas=["arrays", "strings"],
            recent_performance=[
                {"score": 85, "time_spent": 45},
                {"score": 78, "time_spent": 60},
                {"score": 92, "time_spent": 30},
            ],
        )


class TestGenerateAdaptiveAssignment:
    """Tests for generate_adaptive_assignment method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    @pytest.fixture
    def sample_student_profile(self):
        return StudentProfile(
            student_id="student_123",
            skill_levels={"arrays_strings": 3, "linked_lists": 2},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=["recursion"],
            strong_areas=["arrays"],
            recent_performance=[{"score": 85, "time_spent": 45}],
        )

    def test_generate_adaptive_assignment_returns_generated_assignment(
        self, generator, sample_student_profile
    ):
        """Test that generate_adaptive_assignment returns a GeneratedAssignment."""
        result = generator.generate_adaptive_assignment(sample_student_profile)
        assert isinstance(result, GeneratedAssignment)

    def test_generated_assignment_has_required_fields(self, generator, sample_student_profile):
        """Test that generated assignment has all required fields."""
        result = generator.generate_adaptive_assignment(sample_student_profile)
        assert hasattr(result, "assignment_id")
        assert hasattr(result, "title")
        assert hasattr(result, "description")
        assert hasattr(result, "category")
        assert hasattr(result, "difficulty")
        assert hasattr(result, "learning_objectives")
        assert hasattr(result, "problem_statement")
        assert hasattr(result, "starter_code")
        assert hasattr(result, "test_cases")
        assert hasattr(result, "hints")
        assert hasattr(result, "estimated_time")

    def test_generated_assignment_has_valid_difficulty(self, generator, sample_student_profile):
        """Test that generated assignment has valid difficulty level."""
        result = generator.generate_adaptive_assignment(sample_student_profile)
        assert isinstance(result.difficulty, DifficultyLevel)

    def test_generated_assignment_has_valid_category(self, generator, sample_student_profile):
        """Test that generated assignment has valid category."""
        result = generator.generate_adaptive_assignment(sample_student_profile)
        assert isinstance(result.category, ProblemCategory)

    def test_generate_with_specific_category(self, generator, sample_student_profile):
        """Test generating assignment with specific category."""
        result = generator.generate_adaptive_assignment(
            sample_student_profile, category=ProblemCategory.ARRAYS_STRINGS
        )
        assert result.category == ProblemCategory.ARRAYS_STRINGS


class TestSelectOptimalCategory:
    """Tests for _select_optimal_category method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_selects_category_from_weak_areas(self, generator):
        """Test that category selection prioritizes weak areas."""
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="medium",
   preferred_difficulty=3,
            weak_areas=["arrays"],
            strong_areas=[],
            recent_performance=[],
        )
        result = generator._select_optimal_category(profile)
        assert isinstance(result, ProblemCategory)

    def test_returns_valid_category_when_no_weak_areas(self, generator):
        """Test that a valid category is returned when no weak areas."""
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[],
        )
        result = generator._select_optimal_category(profile)
        assert isinstance(result, ProblemCategory)


class TestCalculateTargetDifficulty:
    """Tests for _calculate_target_difficulty method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_increases_difficulty_for_high_success_rate(self, generator):
        """Test that difficulty increases for high success rate."""
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={"arrays_strings": 3},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[
                {"score": 95},
                {"score": 90},
                {"score": 92},
                {"score": 88},
                {"score": 91},
            ],
        )
        result = generator._calculate_target_difficulty(profile, ProblemCategory.ARRAYS_STRINGS)
        assert result.value >= 3

    def test_decreases_difficulty_for_low_success_rate(self, generator):
        """Test that difficulty decreases for low success rate."""
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={"arrays_strings": 3},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[
                {"score": 30},
                {"score": 35},
                {"score": 25},
                {"score": 40},
                {"score": 32},
            ],
        )
        result = generator._calculate_target_difficulty(profile, ProblemCategory.ARRAYS_STRINGS)
        assert result.value <= 3

    def test_returns_valid_difficulty_level(self, generator):
        """Test that returned difficulty is a valid DifficultyLevel."""
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[],
        )
        result = generator._calculate_target_difficulty(profile, ProblemCategory.ARRAYS_STRINGS)
        assert isinstance(result, DifficultyLevel)


class TestCalculateRecentSuccessRate:
    """Tests for _calculate_recent_success_rate method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_calculates_success_rate_correctly(self, generator):
        """Test that success rate is calculated correctly."""
        recent_performance = [
            {"score": 80},
            {"score": 75},
            {"score": 60},
            {"score": 90},
            {"score": 85},
        ]
        result = generator._calculate_recent_success_rate(recent_performance)
        # 4 out of 5 scores are >= 70
        assert result == 0.8

    def test_returns_default_for_empty_performance(self, generator):
        """Test that default rate is returned for empty performance."""
        result = generator._calculate_recent_success_rate([])
        assert result == 0.6

    def test_uses_last_five_submissions(self, generator):
        """Test that only last 5 submissions are used."""
        recent_performance = [
            {"score": 50},
            {"score": 50},
            {"score": 50},
            {"score": 80},
            {"score": 80},
            {"score": 80},
            {"score": 80},
            {"score": 80},
        ]
        result = generator._calculate_recent_success_rate(recent_performance)
        # Last 5 are all 80, so 100% success
        assert result == 1.0


class TestEstimateCompletionTime:
    """Tests for _estimate_completion_time method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_beginner_difficulty_has_shortest_time(self, generator):
        """Test that beginner difficulty has shortest estimated time."""
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="medium",
            preferred_difficulty=1,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[],
        )
        result = generator._estimate_completion_time(DifficultyLevel.BEGINNER, profile)
        assert result == 20

    def test_expert_difficulty_has_longest_time(self, generator):
        """Test that expert difficulty has longest estimated time."""
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="medium",
            preferred_difficulty=5,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[],
        )
        result = generator._estimate_completion_time(DifficultyLevel.EXPERT, profile)
        assert result == 120

    def test_slow_learner_gets_more_time(self, generator):
        """Test that slow learners get more time."""
        slow_profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="slow",
            preferred_difficulty=3,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[],
        )
        fast_profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="fast",
            preferred_difficulty=3,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[],
        )
        slow_time = generator._estimate_completion_time(DifficultyLevel.INTERMEDIATE, slow_profile)
        fast_time = generator._estimate_completion_time(DifficultyLevel.INTERMEDIATE, fast_profile)
        assert slow_time > fast_time


class TestGenerateTestCases:
    """Tests for _generate_test_cases method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_generates_test_cases_list(self, generator):
        """Test that test cases are generated as a list."""
        template = {"concepts": ["arrays"]}
        result = generator._generate_test_cases(template, DifficultyLevel.BEGINNER)
        assert isinstance(result, list)

    def test_more_test_cases_for_higher_difficulty(self, generator):
        """Test that higher difficulty has more test cases."""
        template = {"concepts": ["arrays"]}
        beginner_cases = generator._generate_test_cases(template, DifficultyLevel.BEGINNER)
        advanced_cases = generator._generate_test_cases(template, DifficultyLevel.ADVANCED)
        assert len(advanced_cases) >= len(beginner_cases)


class TestGenerateAdaptiveHints:
    """Tests for _generate_adaptive_hints method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_generates_hints_list(self, generator):
        """Test that hints are generated as a list."""
        template = {"concepts": ["arrays"]}
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=[],
            strong_areas=[],
            recent_performance=[],
        )
        result = generator._generate_adaptive_hints(template, profile)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_adds_hints_for_weak_areas(self, generator):
        """Test that hints are added for weak areas."""
        template = {"concepts": ["hash_maps"]}
        profile = StudentProfile(
            student_id="student_123",
            skill_levels={},
            learning_pace="medium",
            preferred_difficulty=3,
            weak_areas=["hash_maps"],
            strong_areas=[],
            recent_performance=[],
        )
        result = generator._generate_adaptive_hints(template, profile)
        assert any("hash" in hint.lower() for hint in result)


class TestAnalyzeAssignmentEffectiveness:
    """Tests for analyze_assignment_effectiveness method."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_returns_dict(self, generator):
        """Test that effectiveness analysis returns a dictionary."""
        student_results = [
            {"score": 85, "time_spent": 45},
            {"score": 78, "time_spent": 60},
        ]
        result = generator.analyze_assignment_effectiveness("assignment_123", student_results)
        assert isinstance(result, dict)

    def test_has_required_keys(self, generator):
        """Test that effectiveness analysis has required keys."""
        student_results = [{"score": 85, "time_spent": 45}]
        result = generator.analyze_assignment_effectiveness("assignment_123", student_results)
        assert "effectiveness" in result
        assert "needs_adjustment" in result

    def test_returns_unknown_for_empty_results(self, generator):
        """Test that unknown is returned for empty results."""
        result = generator.analyze_assignment_effectiveness("assignment_123", [])
        assert result["effectiveness"] == "unknown"
        assert result["needs_adjustment"] is True

    def test_high_effectiveness_for_good_scores(self, generator):
        """Test that high effectiveness is returned for good scores."""
        student_results = [
            {"score": 90, "time_spent": 30},
            {"score": 85, "time_spent": 35},
            {"score": 88, "time_spent": 40},
        ]
        result = generator.analyze_assignment_effectiveness("assignment_123", student_results)
        assert result["effectiveness"] == "high"

    def test_low_effectiveness_for_poor_scores(self, generator):
        """Test that low effectiveness is returned for poor scores."""
        student_results = [
            {"score": 40, "time_spent": 90},
            {"score": 35, "time_spent": 100},
            {"score": 45, "time_spent": 85},
        ]
        result = generator.analyze_assignment_effectiveness("assignment_123", student_results)
        assert result["effectiveness"] == "low"


class TestProblemContentGeneration:
    """Tests for problem content generation methods."""

    @pytest.fixture
    def generator(self):
        return SmartAssignmentGenerator()

    def test_generate_two_sum_content(self, generator):
        """Test two sum content generation."""
        variation = {"difficulty": 1, "constraint": "array sorted"}
        result = generator._generate_two_sum_content(variation, DifficultyLevel.BEGINNER)
        assert "title" in result
        assert "description" in result
        assert "statement" in result
        assert "objectives" in result
        assert "starter_code" in result

    def test_generate_string_content(self, generator):
        """Test string content generation."""
        variation = {"difficulty": 1, "constraint": "reverse string"}
        result = generator._generate_string_content(variation, DifficultyLevel.BEGINNER)
        assert "title" in result
        assert "reverse" in result["title"].lower()

    def test_generate_list_content(self, generator):
        """Test linked list content generation."""
        variation = {"difficulty": 1, "constraint": "basic insertion/deletion"}
        result = generator._generate_list_content(variation, DifficultyLevel.BEGINNER)
        assert "title" in result
        assert "linked list" in result["title"].lower()
