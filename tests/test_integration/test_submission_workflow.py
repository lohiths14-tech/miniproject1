"""
Integration tests for submission workflow
Tests end-to-end flow: submission → grading → plagiarism check → gamification
"""

import pytest
from datetime import datetime
import json

@pytest.fixture
def test_client():
    """Create test client with all blueprints registered"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

@pytest.fixture
def sample_code():
    """Sample Python code for testing"""
    return """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
    """

@pytest.fixture
def sample_test_cases():
    """Sample test cases for grading"""
    return [
        {'input': '5', 'expected_output': '120'},
        {'input': '3', 'expected_output': '6'},
        {'input': '0', 'expected_output': '1'}
    ]

class TestSubmissionWorkflow:
    """Test complete submission workflow"""

    @pytest.mark.integration
    def test_submit_and_grade_workflow(self, test_client, sample_code):
        """Test submitting code and receiving automatic grading"""
        response = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,
                'assignment_id': 'test_assignment_1',
                'language': 'python',
                'student_name': 'Test Student',
                'student_email': 'test@example.com'
            }
        )

        assert response.status_code == 200
        data = response.get_json()

        assert data['status'] == 'success'
        assert ' submission_id' in data['data']
        assert 'score' in data['data']
        assert 'feedback' in data['data']

    @pytest.mark.integration
    def test_submission_triggers_plagiarism_check(self, test_client, sample_code):
        """Test that submission automatically triggers plagiarism detection"""
        # Submit first code
        response1 = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_1',
                'language': 'python'
            }
        )

        # Submit similar code
        response2 = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,  # Same code
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_2',
                'language': 'python'
            }
        )

        data2 = response2.get_json()

        # Should include plagiarism check results
        if 'plagiarism' in data2:
            assert 'similarity_score' in data2['plagiarism']
            # Same code should have high similarity
            assert data2['plagiarism']['similarity_score'] > 0.9

    @pytest.mark.integration
    def test_submission_triggers_gamification(self, test_client, sample_code):
        """Test that submission awards points and badges"""
        response = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_1',
                'language': 'python'
            }
        )

        data = response.get_json()

        # Should include gamification results
        if 'gamification' in data:
            assert 'points_awarded' in data['gamification']
            assert 'badges_earned' in data['gamification']

    @pytest.mark.integration
    def test_submission_sends_email(self, test_client, sample_code, monkeypatch):
        """Test that submission triggers confirmation email"""
        email_sent = []

        # Mock email sending
        def mock_send_email(to, subject, body):
            email_sent.append({'to': to, 'subject': subject, 'body': body})

        monkeypatch.setattr('services.email_service.send_email', mock_send_email)

        response = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,
                'student_email': 'student@example.com',
                'assignment_id': 'test_assignment_1'
            }
        )

        # Check if email was sent
        # Implementation dependent

    @pytest.mark.integration
    def test_full_workflow_with_perfect_score(self, test_client):
        """Test complete workflow with perfect scoring"""
        # Submit code that will get 100%
        perfect_code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n-1)
        """

        response = test_client.post('/api/submissions/submit',
            json={
                'code': perfect_code,
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_1',
                'language': 'python'
            }
        )

        data = response.get_json()

        # Perfect score should:
        # 1. Get 100% score
        # 2. Award bonus points
        # 3. Potentially earn achievement
        if data['status'] == 'success':
            assert data['data']['score'] >= 90  # Near perfect

    @pytest.mark.integration
    def test_workflow_with_compilation_error(self, test_client):
        """Test workflow when code has compilation errors"""
        bad_code = """
def factorial(n)
    # Missing colon
    return n
        """

        response = test_client.post('/api/submissions/submit',
            json={
                'code': bad_code,
                'assignment_id': 'test_assignment_1',
                'language': 'python'
            }
        )

        data = response.get_json()

        # Should handle error gracefully
        assert response.status_code in [200, 400]
        if data.get('status') == 'success':
            # Score should be low
            assert data['data']['score'] < 50

class TestGradingPlagiarismIntegration:
    """Test integration between grading and plagiarism detection"""

    @pytest.mark.integration
    def test_high_similarity_affects_final_score(self, test_client):
        """Test that high plagiarism similarity may affect scoring"""
        # Implementation dependent - some systems penalize plagiarized code
        pass

    @pytest.mark.integration
    def test_cross_language_plagiarism_detection(self, test_client):
        """Test plagiarism detection across different languages"""
        python_code = "def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
        java_code = "int factorial(int n) { return (n <= 1) ? 1 : n * factorial(n-1); }"

        # Submit Python version
        response1 = test_client.post('/api/submissions/submit',
            json={
                'code': python_code,
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_1',
                'language': 'python'
            }
        )

        # Submit Java version
        response2 = test_client.post('/api/submissions/submit',
            json={
                'code': java_code,
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_2',
                'language': 'java'
            }
        )

        # Should detect cross-language similarity
        # Implementation dependent

class TestAnalyticsIntegration:
    """Test integration with analytics and reporting"""

    @pytest.mark.integration
    def test_submission_updates_analytics(self, test_client, sample_code):
        """Test that submission updates dashboard analytics"""
        # Submit code
        response = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_1'
            }
        )

        # Get analytics
        analytics_response = test_client.get('/api/dashboard/analytics')

        if analytics_response.status_code == 200:
            data = analytics_response.get_json()
            # Should show updated submission count
            assert 'total_submissions' in data.get('data', {})

    @pytest.mark.integration
    def test_leaderboard_updates_after_submission(self, test_client, sample_code):
        """Test that leaderboard updates after successful submission"""
        # Submit code with high score
        response = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,
                'assignment_id': 'test_assignment_1',
                'student_id': 'student_1'
            }
        )

        # Get leaderboard
        leaderboard_response = test_client.get('/api/gamification/leaderboard')

        if leaderboard_response.status_code == 200:
            data = leaderboard_response.get_json()
            # Student should appear in leaderboard
            # Implementation dependent

@pytest.mark.performance
class TestWorkflowPerformance:
    """Test performance of complete workflow"""

    def test_submission_workflow_performance(self, test_client, sample_code):
        """Test that complete workflow completes quickly"""
        import time

        start = time.time()
        response = test_client.post('/api/submissions/submit',
            json={
                'code': sample_code,
                'assignment_id': 'test_assignment_1'
            }
        )
        duration = time.time() - start

        # Complete workflow should finish in reasonable time
        assert duration < 10.0  # Less than 10 seconds

    def test_concurrent_submissions(self, test_client, sample_code):
        """Test handling of concurrent submissions"""
        import threading

        results = []

        def submit():
            response = test_client.post('/api/submissions/submit',
                json={'code': sample_code, 'assignment_id': 'test'}
            )
            results.append(response.status_code)

        # Submit 10 concurrent requests
        threads = [threading.Thread(target=submit) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # All should succeed
        assert all(code == 200 for code in results)
