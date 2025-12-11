"""Tests for Lab Grading Service.

Tests lab-specific grading and rubric application functionality.
Requirements: 2.1, 2.2
"""
import pytest
from services.lab_grading_service import (
    EngineeringLabGradingService,
    LabAssignment,
    LabType,
    CustomizedFeedback,
    lab_grading_service,
)


class TestLabGradingServiceInit:
    """Test suite for service initialization."""

    def test_service_instance_exists(self):
        """Test that global service instance exists."""
        assert lab_grading_service is not None
        assert isinstance(lab_grading_service, EngineeringLabGradingService)

    def test_lab_templates_loaded(self):
        """Test that lab templates are loaded."""
        service = EngineeringLabGradingService()
        assert service.lab_templates is not None
        assert len(service.lab_templates) > 0

    def test_feedback_templates_loaded(self):
        """Test that feedback templates are loaded."""
        service = EngineeringLabGradingService()
        assert service.feedback_templates is not None
        assert len(service.feedback_templates) > 0


class TestLabTemplates:
    """Test suite for lab template functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EngineeringLabGradingService()

    def test_algorithms_template_exists(self):
        """Test that algorithms template exists."""
        templates = self.service.lab_templates
        assert LabType.ALGORITHMS in templates

    def test_data_structures_template_exists(self):
        """Test that data structures template exists."""
        templates = self.service.lab_templates
        assert LabType.DATA_STRUCTURES in templates

    def test_sorting_template_has_test_cases(self):
        """Test that sorting template has test cases."""
        sorting = self.service.lab_templates[LabType.ALGORITHMS]["sorting"]
        assert "test_cases" in sorting
        assert len(sorting["test_cases"]) > 0

    def test_sorting_template_has_criteria(self):
        """Test that sorting template has grading criteria."""
        sorting = self.service.lab_templates[LabType.ALGORITHMS]["sorting"]
        assert "criteria" in sorting
        assert "correctness" in sorting["criteria"]


class TestFeedbackTemplates:
    """Test suite for feedback template functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EngineeringLabGradingService()

    def test_excellent_feedback_template(self):
        """Test excellent feedback template exists."""
        assert "excellent" in self.service.feedback_templates

    def test_good_feedback_template(self):
        """Test good feedback template exists."""
        assert "good" in self.service.feedback_templates

    def test_needs_improvement_template(self):
        """Test needs improvement template exists."""
        assert "needs_improvement" in self.service.feedback_templates

    def test_error_handling_template(self):
        """Test error handling template exists."""
        assert "error_handling" in self.service.feedback_templates


class TestLabAssignmentDataclass:
    """Test suite for LabAssignment dataclass."""

    def test_create_lab_assignment(self):
        """Test creating a LabAssignment instance."""
        assignment = LabAssignment(
            assignment_id="lab_001",
            title="Sorting Algorithm",
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=[{"input": "[3,1,2]", "expected": "[1,2,3]"}],
            evaluation_criteria={"correctness": 50, "efficiency": 30, "quality": 20},
            learning_objectives=["Understand sorting algorithms"],
        )

        assert assignment.assignment_id == "lab_001"
        assert assignment.title == "Sorting Algorithm"
        assert assignment.lab_type == LabType.ALGORITHMS
        assert assignment.max_score == 100

    def test_lab_assignment_test_cases(self):
        """Test LabAssignment test cases field."""
        test_cases = [
            {"input": "[5,3,1]", "expected": "[1,3,5]"},
            {"input": "[]", "expected": "[]"},
        ]
        assignment = LabAssignment(
            assignment_id="lab_002",
            title="Test",
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=test_cases,
            evaluation_criteria={},
            learning_objectives=[],
        )

        assert len(assignment.test_cases) == 2


class TestCustomizedFeedbackDataclass:
    """Test suite for CustomizedFeedback dataclass."""

    def test_create_customized_feedback(self):
        """Test creating a CustomizedFeedback instance."""
        feedback = CustomizedFeedback(
            overall_score=85,
            grade_percentage=85.0,
            execution_results={"passed": 8, "total": 10},
            improvement_suggestions=["Consider edge cases"],
            commendations=["Good code structure"],
            plagiarism_report={"passed": True, "similarity_score": 5},
        )

        assert feedback.overall_score == 85
        assert feedback.grade_percentage == 85.0
        assert len(feedback.improvement_suggestions) == 1
        assert len(feedback.commendations) == 1


class TestLabTypeEnum:
    """Test suite for LabType enum."""

    def test_algorithms_type(self):
        """Test ALGORITHMS lab type."""
        assert LabType.ALGORITHMS.value == "algorithms"

    def test_data_structures_type(self):
        """Test DATA_STRUCTURES lab type."""
        assert LabType.DATA_STRUCTURES.value == "data_structures"

    def test_systems_programming_type(self):
        """Test SYSTEMS_PROGRAMMING lab type."""
        assert LabType.SYSTEMS_PROGRAMMING.value == "systems_programming"

    def test_machine_learning_type(self):
        """Test MACHINE_LEARNING lab type."""
        assert LabType.MACHINE_LEARNING.value == "machine_learning"

    def test_web_development_type(self):
        """Test WEB_DEVELOPMENT lab type."""
        assert LabType.WEB_DEVELOPMENT.value == "web_development"


class TestScoreCalculation:
    """Test suite for score calculation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EngineeringLabGradingService()

    def test_calculate_scores_perfect_execution(self):
        """Test score calculation with perfect execution."""
        execution_results = {
            "passed": 10,
            "total": 10,
            "success_rate": 1.0,
            "details": [],
        }

        class MockAnalysis:
            best_practices_score = 90
            big_o_analysis = {"time_complexity": "O(n)"}

        assignment = LabAssignment(
            assignment_id="test",
            title="Test",
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=[],
            evaluation_criteria={"correctness": 40, "quality": 30, "efficiency": 30},
            learning_objectives=[],
        )

        scores = self.service._calculate_scores(
            execution_results, MockAnalysis(), assignment
        )

        assert "total" in scores
        assert "percentage" in scores
        assert scores["percentage"] <= 100

    def test_calculate_scores_partial_execution(self):
        """Test score calculation with partial execution."""
        execution_results = {
            "passed": 5,
            "total": 10,
            "success_rate": 0.5,
            "details": [],
        }

        class MockAnalysis:
            best_practices_score = 70

        assignment = LabAssignment(
            assignment_id="test",
            title="Test",
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=[],
            evaluation_criteria={"correctness": 40, "quality": 30, "efficiency": 30},
            learning_objectives=[],
        )

        scores = self.service._calculate_scores(
            execution_results, MockAnalysis(), assignment
        )

        assert scores["percentage"] < 100


class TestFeedbackGeneration:
    """Test suite for feedback generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EngineeringLabGradingService()

    def test_generate_feedback_excellent(self):
        """Test feedback generation for excellent scores."""
        scores = {"percentage": 95, "correctness": 38}

        class MockAnalysis:
            optimization_suggestions = []

        assignment = LabAssignment(
            assignment_id="test",
            title="Test",
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=[],
            evaluation_criteria={"correctness": 40},
            learning_objectives=[],
        )

        feedback = self.service._generate_feedback(scores, MockAnalysis(), assignment)

        assert "commendations" in feedback
        assert len(feedback["commendations"]) > 0

    def test_generate_feedback_needs_improvement(self):
        """Test feedback generation for low scores."""
        scores = {"percentage": 50, "correctness": 15}

        class MockAnalysis:
            optimization_suggestions = ["Use better algorithm"]

        assignment = LabAssignment(
            assignment_id="test",
            title="Test",
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=[],
            evaluation_criteria={"correctness": 40},
            learning_objectives=[],
        )

        feedback = self.service._generate_feedback(scores, MockAnalysis(), assignment)

        assert "improvements" in feedback
        assert len(feedback["improvements"]) > 0


class TestErrorFeedback:
    """Test suite for error feedback creation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = EngineeringLabGradingService()

    def test_create_error_feedback(self):
        """Test creating error feedback."""
        feedback = self.service._create_error_feedback("Test error", 100)

        assert isinstance(feedback, CustomizedFeedback)
        assert feedback.overall_score == 0
        assert feedback.grade_percentage == 0
        assert "error" in feedback.execution_results

    def test_error_feedback_has_suggestions(self):
        """Test error feedback includes suggestions."""
        feedback = self.service._create_error_feedback("Syntax error", 100)

        assert len(feedback.improvement_suggestions) > 0
        assert "Syntax error" in feedback.improvement_suggestions[0]

    def test_error_feedback_plagiarism_passed(self):
        """Test error feedback has passing plagiarism report."""
        feedback = self.service._create_error_feedback("Error", 100)

        assert feedback.plagiarism_report["passed"] is True
        assert feedback.plagiarism_report["similarity_score"] == 0

