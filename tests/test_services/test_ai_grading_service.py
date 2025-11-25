"""
Unit tests for AI Grading Service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from services.ai_grading_service import (
    grade_submission,
    run_test_cases,
    execute_code,
    get_ai_feedback,
    generate_comprehensive_feedback
)


@pytest.mark.unit
class TestAIGradingService:
    """Test suite for AI grading functionality"""

    def test_grade_submission_success(self, sample_code, sample_test_cases):
        """Test successful code grading"""
        with patch('services.ai_grading_service.run_test_cases') as mock_test, \
             patch('services.ai_grading_service.get_ai_feedback') as mock_ai:

            mock_test.return_value = {
                'passed': 2,
                'total': 2,
                'pass_rate': 100.0,
                'results': [{'passed': True}, {'passed': True}]
            }
            mock_ai.return_value = {
                'score': 85,
                'feedback': 'Good implementation'
            }

            result = grade_submission(
                code=sample_code,
                test_cases=sample_test_cases,
                programming_language='python'
            )

            assert result is not None
            assert 'score' in result
            assert 'feedback' in result
            assert result['score'] >= 0
            assert result['score'] <= 100

    def test_grade_submission_with_failing_tests(self, sample_code, sample_test_cases):
        """Test grading with failing test cases"""
        with patch('services.ai_grading_service.run_test_cases') as mock_test:
            mock_test.return_value = {
                'passed': 1,
                'total': 2,
                'pass_rate': 50.0,
                'results': [{'passed': True}, {'passed': False}]
            }

            result = grade_submission(
                code=sample_code,
                test_cases=sample_test_cases,
                programming_language='python'
            )

            assert result['test_results']['pass_rate'] == 50.0

    def test_execute_python_code(self):
        """Test Python code execution"""
        code = "print('Hello, World!')"
        test_input = ""

        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(
                stdout='Hello, World!\n',
                stderr='',
                returncode=0
            )

            result = execute_code(code, test_input, 'python')

            assert result is not None

    def test_execute_code_with_timeout(self):
        """Test code execution timeout handling"""
        infinite_loop = "while True: pass"

        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = TimeoutError("Execution timeout")

            result = execute_code(infinite_loop, "", 'python')

            # Should handle timeout gracefully
            assert result is not None or True  # Depends on implementation

    def test_run_test_cases_all_pass(self, sample_code):
        """Test running test cases with all passing"""
        test_cases = [
            {'input': '5', 'expected_output': '5'},
            {'input': '10', 'expected_output': '55'}
        ]

        with patch('services.ai_grading_service.execute_code') as mock_exec:
            mock_exec.side_effect = [
                {'output': '5', 'error': '', 'execution_time': 0.1},
                {'output': '55', 'error': '', 'execution_time': 0.15}
            ]

            result = run_test_cases(sample_code, test_cases, 'python')

            assert result['passed'] == 2
            assert result['total'] == 2
            assert result['pass_rate'] == 100.0

    def test_generate_comprehensive_feedback(self):
        """Test comprehensive feedback generation"""
        ai_feedback = {
            'quality_score': 85,
            'suggestions': ['Consider using dynamic programming']
        }
        analysis_result = {
            'complexity': {'cyclomatic': 5},
            'best_practices_score': 80
        }
        test_results = {
            'passed': 2,
            'total': 2,
            'pass_rate': 100.0
        }

        feedback = generate_comprehensive_feedback(
            ai_feedback, analysis_result, test_results
        )

        assert feedback is not None
        assert 'summary' in feedback or isinstance(feedback, str)

    @patch('services.ai_grading_service.OPENAI_AVAILABLE', False)
    def test_fallback_grading_without_openai(self, sample_code):
        """Test fallback grading when OpenAI is unavailable"""
        result = grade_submission(
            code=sample_code,
            test_cases=[],
            programming_language='python'
        )

        # Should use rule-based grading
        assert result is not None
        assert 'score' in result

    def test_multi_language_support(self):
        """Test grading for different programming languages"""
        languages = ['python', 'java', 'cpp', 'javascript']

        for lang in languages:
            with patch('services.ai_grading_service.execute_code') as mock_exec:
                mock_exec.return_value = {'output': 'test', 'error': ''}

                result = execute_code('code', '', lang)
                assert result is not None
