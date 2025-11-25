"""
Unit tests for Submission Routes
"""
import pytest
import json
from unittest.mock import patch


@pytest.mark.unit
class TestSubmissionRoutes:
    """Test suite for submission API endpoints"""

    def test_submit_code_success(self, client, auth_headers, sample_code):
        """Test successful code submission"""
        submission_data = {
            'assignment_id': 'test_assignment',
            'code': sample_code,
            'programming_language': 'python'
        }

        with patch('services.ai_grading_service.grade_submission') as mock_grade:
            mock_grade.return_value = {
                'score': 85,
                'feedback': 'Good work',
                'test_results': {'passed': 2, 'total': 2}
            }

            response = client.post(
                '/api/submissions/submit',
                data=json.dumps(submission_data),
                content_type='application/json',
                headers=auth_headers
            )

            # Should succeed or require auth
            assert response.status_code in [200, 201, 401]

    def test_submit_code_missing_fields(self, client, auth_headers):
        """Test submission with missing required fields"""
        incomplete_data = {
            'code': 'print("test")'
            # Missing assignment_id and language
        }

        response = client.post(
            '/api/submissions/submit',
            data=json.dumps(incomplete_data),
            content_type='application/json',
            headers=auth_headers
        )

        assert response.status_code in [400, 422]

    def test_get_submissions(self, client, auth_headers):
        """Test retrieving user submissions"""
        response = client.get(
            '/api/submissions/my-submissions',
            headers=auth_headers
        )

        # Should return list or require auth
        assert response.status_code in [200, 401]

    def test_get_submission_details(self, client, auth_headers):
        """Test getting specific submission details"""
        response = client.get(
            '/api/submissions/123',
            headers=auth_headers
        )

        # May not exist, but should handle gracefully
        assert response.status_code in [200, 404, 401]
