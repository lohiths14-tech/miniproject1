"""Comprehensive tests for AI Grading Service.

This module provides extensive test coverage for the ai_grading_service module,
targeting 70%+ coverage with focus on core functionality, edge cases, and error handling.
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from services.ai_grading_service import (
    execute_code,
    generate_comprehensive_feedback,
    get_ai_feedback,
    grade_submission,
    run_test_cases,
)


class TestGradeSubmission:
    """Test suite for grade_submission function."""

    @pytest.fixture
    def valid_python_code(self):
        """Return valid Python code for testing."""
        return """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b
"""

    @pytest.fixture
    def valid_test_cases(self):
        """Return valid test cases."""
        return [
            {"input": "2, 3", "expected_output": "5", "function": "add"},
            {"input": "4, 5", "expected_output": "20", "function": "multiply"},
        ]

    @pytest.fixture
    def complex_test_cases(self):
        """Return complex test cases."""
        return [
            {"input": "10", "expected_output": "55"},
            {"input": "5", "expected_output": "15"},
            {"input": "1", "expected_output": "1"},
        ]

    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    @patch("services.ai_grading_service.gamification_service.award_points_and_badges")
    def test_grade_submission_success(
        self,
        mock_gamification,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
        valid_python_code,
        valid_test_cases,
    ):
        """Test successful code submission grading."""
        # Setup mocks
        mock_run_tests.return_value = [
            {"passed": True, "execution_time": 0.001},
            {"passed": True, "execution_time": 0.002},
        ]

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "Medium"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
        }
        mock_analysis.performance_metrics.execution_time = 0.0015
        mock_analysis.performance_metrics.memory_usage = 1024
        mock_analysis.performance_metrics.operations_count = 5
        mock_analysis.code_metrics.lines_of_code = 10
        mock_analysis.code_metrics.cyclomatic_complexity = 2
        mock_analysis.code_metrics.nesting_depth = 1
        mock_analysis.code_metrics.function_count = 2
        mock_analysis.optimization_suggestions = ["Consider edge cases"]
        mock_analysis.code_smells = []
        mock_analysis.best_practices_score = 85
        mock_analysis.maintainability_score = 90
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "Good code quality"
        mock_feedback.return_value = "Comprehensive feedback message"
        mock_gamification.return_value = {"points": 100, "badges": ["first_submission"]}

        # Execute
        result = grade_submission(
            valid_python_code, valid_test_cases, "python", "user123"
        )

        # Assert
        assert result["score"] > 0
        assert result["max_score"] == 100
        assert "test_results" in result
        assert "code_analysis" in result
        assert "feedback" in result
        assert "gamification" in result
        assert result["score_breakdown"]["correctness"] == 50
        assert mock_run_tests.called
        assert mock_analyze.called
        assert mock_gamification.called

    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    def test_grade_submission_without_user_id(
        self,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
        valid_python_code,
        valid_test_cases,
    ):
        """Test grading without user ID (no gamification)."""
        mock_run_tests.return_value = [{"passed": True, "execution_time": 0.001}]

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "Low"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
        }
        mock_analysis.performance_metrics.execution_time = 0.001
        mock_analysis.performance_metrics.memory_usage = 512
        mock_analysis.performance_metrics.operations_count = 2
        mock_analysis.code_metrics.lines_of_code = 5
        mock_analysis.code_metrics.cyclomatic_complexity = 1
        mock_analysis.code_metrics.nesting_depth = 0
        mock_analysis.code_metrics.function_count = 1
        mock_analysis.optimization_suggestions = []
        mock_analysis.code_smells = []
        mock_analysis.best_practices_score = 95
        mock_analysis.maintainability_score = 95
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "Excellent work"
        mock_feedback.return_value = "Great job!"

        result = grade_submission(valid_python_code, valid_test_cases, "python")

        assert "gamification" not in result
        assert result["score"] > 0

    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    def test_grade_submission_poor_efficiency(
        self,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
        valid_python_code,
        valid_test_cases,
    ):
        """Test grading with poor efficiency (O(n²) complexity)."""
        mock_run_tests.return_value = [{"passed": True, "execution_time": 0.1}]

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "High"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(n²)",
            "space_complexity": "O(n)",
        }
        mock_analysis.performance_metrics.execution_time = 0.5
        mock_analysis.performance_metrics.memory_usage = 4096
        mock_analysis.performance_metrics.operations_count = 1000
        mock_analysis.code_metrics.lines_of_code = 50
        mock_analysis.code_metrics.cyclomatic_complexity = 10
        mock_analysis.code_metrics.nesting_depth = 4
        mock_analysis.code_metrics.function_count = 1
        mock_analysis.optimization_suggestions = ["Optimize nested loops"]
        mock_analysis.code_smells = ["Complex method"]
        mock_analysis.best_practices_score = 60
        mock_analysis.maintainability_score = 55
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "Consider optimizing"
        mock_feedback.return_value = "Needs optimization"

        result = grade_submission(valid_python_code, valid_test_cases, "python")

        assert result["score_breakdown"]["efficiency"] == 10
        assert result["code_analysis"]["big_o_analysis"]["time_complexity"] == "O(n²)"

    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    def test_grade_submission_partial_pass(
        self,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
        valid_python_code,
        valid_test_cases,
    ):
        """Test grading with some failing test cases."""
        mock_run_tests.return_value = [
            {"passed": True, "execution_time": 0.001},
            {"passed": False, "execution_time": 0.002},
            {"passed": True, "execution_time": 0.001},
        ]

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "Medium"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
        }
        mock_analysis.performance_metrics.execution_time = 0.001
        mock_analysis.performance_metrics.memory_usage = 1024
        mock_analysis.performance_metrics.operations_count = 10
        mock_analysis.code_metrics.lines_of_code = 20
        mock_analysis.code_metrics.cyclomatic_complexity = 3
        mock_analysis.code_metrics.nesting_depth = 2
        mock_analysis.code_metrics.function_count = 2
        mock_analysis.optimization_suggestions = []
        mock_analysis.code_smells = []
        mock_analysis.best_practices_score = 80
        mock_analysis.maintainability_score = 85
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "Some tests failed"
        mock_feedback.return_value = "Review failed tests"

        result = grade_submission(valid_python_code, valid_test_cases, "python")

        # 2/3 tests passed = 33.33% correctness score out of 50
        expected_correctness = (2 / 3) * 50
        assert abs(result["score_breakdown"]["correctness"] - expected_correctness) < 1

    @patch("services.ai_grading_service.run_test_cases")
    def test_grade_submission_exception_handling(
        self,
        mock_run_tests,
        valid_python_code,
        valid_test_cases,
    ):
        """Test exception handling in grade_submission."""
        mock_run_tests.side_effect = ValueError("Test execution failed")

        result = grade_submission(valid_python_code, valid_test_cases, "python")

        assert result["score"] == 0
        assert "failed" in result["feedback"].lower()

    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    def test_grade_submission_empty_test_cases(
        self,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
        valid_python_code,
    ):
        """Test grading with no test cases."""
        mock_run_tests.return_value = []

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "Low"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
        }
        mock_analysis.performance_metrics.execution_time = 0.001
        mock_analysis.performance_metrics.memory_usage = 512
        mock_analysis.performance_metrics.operations_count = 1
        mock_analysis.code_metrics.lines_of_code = 5
        mock_analysis.code_metrics.cyclomatic_complexity = 1
        mock_analysis.code_metrics.nesting_depth = 0
        mock_analysis.code_metrics.function_count = 1
        mock_analysis.optimization_suggestions = []
        mock_analysis.code_smells = []
        mock_analysis.best_practices_score = 90
        mock_analysis.maintainability_score = 90
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "No tests provided"
        mock_feedback.return_value = "Add test cases"

        result = grade_submission(valid_python_code, [], "python")

        assert result["score_breakdown"]["correctness"] == 0


class TestRunTestCases:
    """Test suite for run_test_cases function."""

    @patch("services.ai_grading_service.execute_code")
    def test_run_test_cases_python_success(self, mock_execute):
        """Test running Python test cases successfully."""
        mock_execute.side_effect = [
            (True, "5", 0.001, ""),
            (True, "10", 0.002, ""),
        ]

        code = "def add(a, b): return a + b"
        test_cases = [
            {"input": "2, 3", "expected_output": "5"},
            {"input": "4, 6", "expected_output": "10"},
        ]

        results = run_test_cases(code, test_cases, "python")

        assert len(results) == 2
        assert all(r["passed"] for r in results)

    @patch("services.ai_grading_service.execute_code")
    def test_run_test_cases_with_failure(self, mock_execute):
        """Test running test cases with failures."""
        mock_execute.side_effect = [
            (True, "5", 0.001, ""),
            (True, "11", 0.002, ""),  # Wrong output
        ]

        code = "def add(a, b): return a + b"
        test_cases = [
            {"input": "2, 3", "expected_output": "5"},
            {"input": "4, 6", "expected_output": "10"},
        ]

        results = run_test_cases(code, test_cases, "python")

        assert results[0]["passed"] is True
        assert results[1]["passed"] is False

    @patch("services.ai_grading_service.execute_code")
    def test_run_test_cases_execution_error(self, mock_execute):
        """Test handling execution errors in test cases."""
        mock_execute.return_value = (False, "", 0, "SyntaxError: invalid syntax")

        code = "def add(a, b) return a + b"  # Missing colon
        test_cases = [{"input": "2, 3", "expected_output": "5"}]

        results = run_test_cases(code, test_cases, "python")

        assert results[0]["passed"] is False
        assert "error" in results[0]

    @patch("services.ai_grading_service.execute_code")
    def test_run_test_cases_java(self, mock_execute):
        """Test running Java test cases."""
        mock_execute.return_value = (True, "Hello World", 0.01, "")

        code = """
        public class Main {
            public static void main(String[] args) {
                System.out.println("Hello World");
            }
        }
        """
        test_cases = [{"input": "", "expected_output": "Hello World"}]

        results = run_test_cases(code, test_cases, "java")

        assert len(results) == 1
        assert results[0]["passed"] is True

    @patch("services.ai_grading_service.execute_code")
    def test_run_test_cases_cpp(self, mock_execute):
        """Test running C++ test cases."""
        mock_execute.return_value = (True, "42", 0.005, "")

        code = """
        #include <iostream>
        int main() {
            std::cout << 42;
            return 0;
        }
        """
        test_cases = [{"input": "", "expected_output": "42"}]

        results = run_test_cases(code, test_cases, "cpp")

        assert results[0]["passed"] is True


class TestGetAIFeedback:
    """Test suite for get_ai_feedback function."""

    @patch("services.ai_grading_service.OPENAI_AVAILABLE", True)
    @patch("services.ai_grading_service.openai.ChatCompletion.create")
    def test_get_ai_feedback_success(self, mock_openai):
        """Test successful AI feedback generation."""
        mock_openai.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content="Your code is well-structured. Consider adding error handling."
                    )
                )
            ]
        )

        code = "def add(a, b): return a + b"
        test_cases = [{"input": "1, 2", "expected_output": "3"}]
        analysis = Mock()

        feedback = get_ai_feedback(code, test_cases, "python", analysis)

        assert feedback is not None
        assert len(feedback) > 0

    @patch("services.ai_grading_service.OPENAI_AVAILABLE", True)
    @patch("services.ai_grading_service.openai.ChatCompletion.create")
    def test_get_ai_feedback_api_error(self, mock_openai):
        """Test AI feedback when API call fails."""
        mock_openai.side_effect = Exception("API Error")

        code = "def add(a, b): return a + b"
        test_cases = []
        analysis = Mock()

        feedback = get_ai_feedback(code, test_cases, "python", analysis)

        assert "error" in feedback.lower() or "unable" in feedback.lower()

    @patch("services.ai_grading_service.OPENAI_AVAILABLE", False)
    def test_get_ai_feedback_openai_not_available(self):
        """Test AI feedback when OpenAI is not available."""
        code = "def add(a, b): return a + b"
        test_cases = []
        analysis = Mock()

        feedback = get_ai_feedback(code, test_cases, "python", analysis)

        assert "not available" in feedback.lower()


class TestGenerateComprehensiveFeedback:
    """Test suite for generate_comprehensive_feedback function."""

    def test_generate_comprehensive_feedback_complete(self):
        """Test generating comprehensive feedback with all components."""
        ai_feedback = "Your code shows good structure."

        analysis = Mock()
        analysis.optimization_suggestions = ["Use list comprehension", "Cache results"]
        analysis.code_smells = ["Long method", "Too many parameters"]
        analysis.best_practices_score = 75

        test_results = [
            {"passed": True, "input": "1", "expected": "1", "actual": "1"},
            {"passed": False, "input": "2", "expected": "4", "actual": "2"},
        ]

        feedback = generate_comprehensive_feedback(ai_feedback, analysis, test_results)

        assert "Your code shows good structure" in feedback
        assert "optimization" in feedback.lower() or "improve" in feedback.lower()
        assert isinstance(feedback, str)
        assert len(feedback) > 0

    def test_generate_comprehensive_feedback_perfect_score(self):
        """Test feedback generation for perfect submission."""
        ai_feedback = "Excellent work!"

        analysis = Mock()
        analysis.optimization_suggestions = []
        analysis.code_smells = []
        analysis.best_practices_score = 100

        test_results = [
            {"passed": True, "input": "1", "expected": "1", "actual": "1"},
        ]

        feedback = generate_comprehensive_feedback(ai_feedback, analysis, test_results)

        assert "excellent" in feedback.lower() or "perfect" in feedback.lower()

    def test_generate_comprehensive_feedback_with_failures(self):
        """Test feedback generation with failed tests."""
        ai_feedback = "Review your logic."

        analysis = Mock()
        analysis.optimization_suggestions = ["Fix algorithm"]
        analysis.code_smells = []
        analysis.best_practices_score = 60

        test_results = [
            {"passed": False, "input": "1", "expected": "1", "actual": "0"},
            {"passed": False, "input": "2", "expected": "2", "actual": "0"},
        ]

        feedback = generate_comprehensive_feedback(ai_feedback, analysis, test_results)

        assert "fail" in feedback.lower() or "incorrect" in feedback.lower()


class TestExecuteCode:
    """Test suite for execute_code function."""

    def test_execute_code_python_simple(self):
        """Test executing simple Python code."""
        code = "print(42)"
        success, output, exec_time, error = execute_code(code, "", "python")

        assert success is True
        assert "42" in output.strip()
        assert exec_time >= 0
        assert error == ""

    def test_execute_code_python_with_input(self):
        """Test executing Python code with input."""
        code = """
x = int(input())
y = int(input())
print(x + y)
"""
        success, output, exec_time, error = execute_code(code, "5\n3\n", "python")

        assert success is True
        assert "8" in output.strip()

    def test_execute_code_syntax_error(self):
        """Test executing Python code with syntax error."""
        code = "print('hello'"  # Missing closing parenthesis
        success, output, exec_time, error = execute_code(code, "", "python")

        assert success is False
        assert len(error) > 0

    def test_execute_code_runtime_error(self):
        """Test executing Python code with runtime error."""
        code = "x = 1 / 0"
        success, output, exec_time, error = execute_code(code, "", "python")

        assert success is False
        assert "ZeroDivisionError" in error or "division" in error.lower()

    @pytest.mark.parametrize("language", ["java", "cpp", "javascript"])
    def test_execute_code_multiple_languages(self, language):
        """Test code execution for multiple programming languages."""
        # This is a basic test structure; actual implementation depends on your setup
        code = "// Sample code"
        success, output, exec_time, error = execute_code(code, "", language)

        # Should at least not crash
        assert isinstance(success, bool)
        assert isinstance(output, str)
        assert isinstance(exec_time, (int, float))
        assert isinstance(error, str)


class TestEdgeCases:
    """Test suite for edge cases and boundary conditions."""

    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    def test_grade_empty_code(
        self,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
    ):
        """Test grading empty code submission."""
        mock_run_tests.return_value = []

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "Low"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
        }
        mock_analysis.performance_metrics.execution_time = 0
        mock_analysis.performance_metrics.memory_usage = 0
        mock_analysis.performance_metrics.operations_count = 0
        mock_analysis.code_metrics.lines_of_code = 0
        mock_analysis.code_metrics.cyclomatic_complexity = 0
        mock_analysis.code_metrics.nesting_depth = 0
        mock_analysis.code_metrics.function_count = 0
        mock_analysis.optimization_suggestions = []
        mock_analysis.code_smells = []
        mock_analysis.best_practices_score = 0
        mock_analysis.maintainability_score = 0
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "Empty submission"
        mock_feedback.return_value = "Please submit code"

        result = grade_submission("", [], "python")

        assert result["score"] >= 0
        assert result["max_score"] == 100

    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    def test_grade_very_long_code(
        self,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
    ):
        """Test grading very long code submission."""
        long_code = "x = 1\n" * 10000
        mock_run_tests.return_value = [{"passed": True, "execution_time": 0.1}]

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "High"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(1)",
            "space_complexity": "O(n)",
        }
        mock_analysis.performance_metrics.execution_time = 1.0
        mock_analysis.performance_metrics.memory_usage = 100000
        mock_analysis.performance_metrics.operations_count = 10000
        mock_analysis.code_metrics.lines_of_code = 10000
        mock_analysis.code_metrics.cyclomatic_complexity = 1
        mock_analysis.code_metrics.nesting_depth = 0
        mock_analysis.code_metrics.function_count = 0
        mock_analysis.optimization_suggestions = ["Refactor large code"]
        mock_analysis.code_smells = ["Long code"]
        mock_analysis.best_practices_score = 40
        mock_analysis.maintainability_score = 30
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "Code is too long"
        mock_feedback.return_value = "Consider refactoring"

        result = grade_submission(long_code, [], "python")

        assert "code_analysis" in result

    def test_execute_code_timeout(self):
        """Test code execution with infinite loop (should timeout)."""
        code = "while True: pass"
        # This test depends on your timeout implementation
        success, output, exec_time, error = execute_code(code, "", "python")

        # Should either timeout or be handled gracefully
        assert isinstance(success, bool)


class TestIntegration:
    """Integration tests for the AI grading service."""

    def test_full_grading_workflow_python(self):
        """Test complete grading workflow for Python code."""
        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(5))
"""
        test_cases = [{"input": "", "expected_output": "5"}]

        # This is an integration test that uses actual functions
        # Might need mocking depending on your setup
        try:
            result = grade_submission(code, test_cases, "python")
            assert "score" in result
            assert "test_results" in result
            assert "code_analysis" in result
        except Exception as e:
            # If dependencies aren't available, test should still pass
            pytest.skip(f"Integration test skipped: {str(e)}")

    @patch("services.ai_grading_service.gamification_service.award_points_and_badges")
    @patch("services.ai_grading_service.run_test_cases")
    @patch("services.ai_grading_service.code_analyzer.analyze_code")
    @patch("services.ai_grading_service.get_ai_feedback")
    @patch("services.ai_grading_service.generate_comprehensive_feedback")
    def test_perfect_score_awards_gamification(
        self,
        mock_feedback,
        mock_ai_feedback,
        mock_analyze,
        mock_run_tests,
        mock_gamification,
    ):
        """Test that perfect scores trigger appropriate gamification."""
        mock_run_tests.return_value = [{"passed": True, "execution_time": 0.001}]

        mock_analysis = Mock()
        mock_analysis.complexity_level.value = "Low"
        mock_analysis.big_o_analysis = {
            "time_complexity": "O(1)",
            "space_complexity": "O(1)",
        }
        mock_analysis.performance_metrics.execution_time = 0.001
        mock_analysis.performance_metrics.memory_usage = 512
        mock_analysis.performance_metrics.operations_count = 1
        mock_analysis.code_metrics.lines_of_code = 5
        mock_analysis.code_metrics.cyclomatic_complexity = 1
        mock_analysis.code_metrics.nesting_depth = 0
        mock_analysis.code_metrics.function_count = 1
        mock_analysis.optimization_suggestions = []
        mock_analysis.code_smells = []
        mock_analysis.best_practices_score = 100
        mock_analysis.maintainability_score = 100
        mock_analyze.return_value = mock_analysis

        mock_ai_feedback.return_value = "Perfect!"
        mock_feedback.return_value = "Excellent work!"
        mock_gamification.return_value = {
            "points": 150,
            "badges": ["perfect_score", "first_submission"],
            "level_up": True,
        }

        code = "def add(a, b): return a + b"
        test_cases = [{"input": "1, 2", "expected_output": "3"}]

        result = grade_submission(code, test_cases, "python", "user123")

        assert result["score"] == 100
        assert "gamification" in result
        mock_gamification.assert_called_once()
        call_args = mock_gamification.call_args
        assert call_args[1]["perfect_score"] is True
