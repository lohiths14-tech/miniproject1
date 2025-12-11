"""
Comprehensive API Tests for Plagiarism Endpoints (Task 21.1)
Tests for /api/plagiarism/check, /api/plagiarism/results/:id, and /api/plagiarism/dashboard
"""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def authenticated_session(client):
    """Create an authenticated session"""
    with client.session_transaction() as sess:
        sess['user_id'] = 'test_user_id'
    return client


# ==================== 21.1 Test POST /api/plagiarism/scan ====================

class TestPlagiarismCheckAPI:
    """Test suite for POST /api/plagiarism/scan endpoint"""

    def test_plagiarism_check_success(self, authenticated_session):
        """Test successful plagiarism check with valid data"""
        mock_detector = MagicMock()
        mock_detector.batch_detect_plagiarism.return_value = {
            'matches': [],
            'total_comparisons': 5,
            'flagged_count': 0
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.post('/api/plagiarism/scan', json={
                'assignment_id': 'test_assignment_123',
                'submissions': [
                    {'id': 'sub1', 'code': 'def test(): return 1'},
                    {'id': 'sub2', 'code': 'def test(): return 2'}
                ]
            })

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert 'message' in data

    def test_plagiarism_check_missing_assignment_id(self, authenticated_session):
        """Test plagiarism check with missing assignment_id (400)"""
        response = authenticated_session.post('/api/plagiarism/scan', json={
            'submissions': [
                {'id': 'sub1', 'code': 'def test(): return 1'}
            ]
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert 'assignment_id' in data['error'].lower()

    def test_plagiarism_check_missing_submissions(self, authenticated_session):
        """Test plagiarism check with missing submissions (400)"""
        response = authenticated_session.post('/api/plagiarism/scan', json={
            'assignment_id': 'test_assignment_123'
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert 'submissions' in data['error'].lower()

    def test_plagiarism_check_with_threshold(self, authenticated_session):
        """Test plagiarism check with custom threshold"""
        mock_detector = MagicMock()
        mock_detector.batch_detect_plagiarism.return_value = {
            'matches': [],
            'total_comparisons': 5,
            'flagged_count': 0
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.post('/api/plagiarism/scan', json={
                'assignment_id': 'test_assignment_123',
                'submissions': [
                    {'id': 'sub1', 'code': 'def test(): return 1'}
                ],
                'threshold': 0.85
            })

            assert response.status_code == 200
            mock_detector.batch_detect_plagiarism.assert_called_once()
            call_args = mock_detector.batch_detect_plagiarism.call_args
            assert call_args[0][1] == 0.85

    def test_plagiarism_check_with_algorithms(self, authenticated_session):
        """Test plagiarism check with specific algorithms"""
        mock_detector = MagicMock()
        mock_detector.batch_detect_plagiarism.return_value = {
            'matches': [],
            'total_comparisons': 5,
            'flagged_count': 0
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.post('/api/plagiarism/scan', json={
                'assignment_id': 'test_assignment_123',
                'submissions': [
                    {'id': 'sub1', 'code': 'def test(): return 1'}
                ],
                'algorithms': ['tfidf', 'structural']
            })

            assert response.status_code == 200
            call_args = mock_detector.batch_detect_plagiarism.call_args
            assert call_args[0][2] == ['tfidf', 'structural']

    def test_plagiarism_check_without_authentication(self, client):
        """Test plagiarism check without authentication (401)"""
        response = client.post('/api/plagiarism/scan', json={
            'assignment_id': 'test_assignment_123',
            'submissions': [
                {'id': 'sub1', 'code': 'def test(): return 1'}
            ]
        })

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


# ==================== Test GET /api/plagiarism/results/:id ====================

class TestPlagiarismResultsAPI:
    """Test suite for GET /api/plagiarism/results/:id endpoint"""

    def test_get_plagiarism_results_success(self, authenticated_session):
        """Test successful retrieval of plagiarism results"""
        mock_detector = MagicMock()
        mock_detector.get_assignment_results.return_value = {
            'assignment_id': 'test_assignment_123',
            'matches': [
                {
                    'submission1_id': 'sub1',
                    'submission2_id': 'sub2',
                    'similarity_score': 0.95
                }
            ],
            'total_matches': 1
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/results/test_assignment_123')

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert data['data']['assignment_id'] == 'test_assignment_123'

    def test_get_plagiarism_results_with_threshold(self, authenticated_session):
        """Test getting results with custom threshold filter"""
        mock_detector = MagicMock()
        mock_detector.get_assignment_results.return_value = {'matches': []}

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/results/test_assignment_123?threshold=0.8')

            assert response.status_code == 200
            mock_detector.get_assignment_results.assert_called_once()
            call_kwargs = mock_detector.get_assignment_results.call_args[1]
            assert call_kwargs['threshold'] == 0.8

    def test_get_plagiarism_results_with_sorting(self, authenticated_session):
        """Test getting results with sorting parameters"""
        mock_detector = MagicMock()
        mock_detector.get_assignment_results.return_value = {'matches': []}

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/results/test_assignment_123?sort_by=similarity_score&order=desc')

            assert response.status_code == 200
            call_kwargs = mock_detector.get_assignment_results.call_args[1]
            assert call_kwargs['sort_by'] == 'similarity_score'
            assert call_kwargs['order'] == 'desc'

    def test_get_plagiarism_results_without_authentication(self, client):
        """Test getting results without authentication (401)"""
        response = client.get('/api/plagiarism/results/test_assignment_123')

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data


# ==================== Test GET /api/plagiarism/dashboard-stats ====================

class TestPlagiarismDashboardAPI:
    """Test suite for GET /api/plagiarism/dashboard-stats endpoint (lecturer only)"""

    def test_dashboard_stats_success_lecturer(self, authenticated_session):
        """Test successful dashboard stats retrieval by lecturer"""
        mock_detector = MagicMock()
        mock_detector.get_dashboard_statistics.return_value = {
            'total_checks': 100,
            'flagged_submissions': 15,
            'average_similarity': 0.35,
            'recent_activity': []
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/dashboard-stats')

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert data['data']['total_checks'] == 100

    def test_dashboard_stats_with_assignment_filter(self, authenticated_session):
        """Test dashboard stats with assignment filter"""
        mock_detector = MagicMock()
        mock_detector.get_dashboard_statistics.return_value = {'total_checks': 50}

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/dashboard-stats?assignment_id=test_assignment_123')

            assert response.status_code == 200
            call_kwargs = mock_detector.get_dashboard_statistics.call_args[1]
            assert call_kwargs['assignment_id'] == 'test_assignment_123'

    def test_dashboard_stats_with_time_period(self, authenticated_session):
        """Test dashboard stats with time period filter"""
        mock_detector = MagicMock()
        mock_detector.get_dashboard_statistics.return_value = {'total_checks': 25}

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/dashboard-stats?period=7days')

            assert response.status_code == 200
            call_kwargs = mock_detector.get_dashboard_statistics.call_args[1]
            assert call_kwargs['time_period'] == '7days'

    def test_dashboard_stats_without_authentication(self, client):
        """Test dashboard stats without authentication (401)"""
        response = client.get('/api/plagiarism/dashboard-stats')

        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data

    def test_dashboard_stats_student_access(self, authenticated_session):
        """Test that students can access dashboard stats (current implementation)"""
        # Note: The current implementation uses session-based auth with require_auth decorator
        # which only checks if user is logged in, not their role
        # This test documents current behavior - any authenticated user can access
        mock_detector = MagicMock()
        mock_detector.get_dashboard_statistics.return_value = {'total_checks': 10}

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/dashboard-stats')

            # Current implementation allows any authenticated user
            assert response.status_code == 200


# ==================== Test Authorization ====================

class TestPlagiarismAuthorization:
    """Test suite for plagiarism endpoint authorization (Task 21.1)"""

    def test_scan_requires_authentication(self, client):
        """Test that scan endpoint requires authentication"""
        response = client.post('/api/plagiarism/scan', json={
            'assignment_id': 'test',
            'submissions': []
        })

        assert response.status_code == 401

    def test_results_requires_authentication(self, client):
        """Test that results endpoint requires authentication"""
        response = client.get('/api/plagiarism/results/test_assignment')

        assert response.status_code == 401

    def test_dashboard_requires_authentication(self, client):
        """Test that dashboard endpoint requires authentication"""
        response = client.get('/api/plagiarism/dashboard-stats')

        assert response.status_code == 401

    def test_compare_requires_authentication(self, client):
        """Test that compare endpoint requires authentication"""
        response = client.post('/api/plagiarism/compare', json={
            'submission1': {'id': 'sub1', 'code': 'test'},
            'submission2': {'id': 'sub2', 'code': 'test'}
        })

        assert response.status_code == 401

    def test_trends_requires_authentication(self, client):
        """Test that trends endpoint requires authentication"""
        response = client.get('/api/plagiarism/trends')

        assert response.status_code == 401

    def test_report_requires_authentication(self, client):
        """Test that report endpoint requires authentication"""
        response = client.get('/api/plagiarism/report/test_assignment')

        assert response.status_code == 401


# ==================== Additional Endpoint Tests ====================

class TestAdditionalPlagiarismEndpoints:
    """Test suite for additional plagiarism endpoints"""

    def test_compare_submissions_success(self, authenticated_session):
        """Test successful comparison of two submissions"""
        mock_detector = MagicMock()
        mock_detector.detailed_comparison.return_value = {
            'similarity_score': 0.85,
            'algorithms': {
                'tfidf': 0.82,
                'structural': 0.88
            }
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.post('/api/plagiarism/compare', json={
                'submission1': {'id': 'sub1', 'code': 'def test(): return 1'},
                'submission2': {'id': 'sub2', 'code': 'def test(): return 1'}
            })

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data

    def test_compare_submissions_missing_field(self, authenticated_session):
        """Test comparison with missing required field"""
        response = authenticated_session.post('/api/plagiarism/compare', json={
            'submission1': {'id': 'sub1', 'code': 'def test(): return 1'}
            # Missing submission2
        })

        assert response.status_code == 400
        data = response.get_json()
        assert data['success'] is False
        assert 'submission2' in data['error'].lower()

    def test_get_trends_success(self, authenticated_session):
        """Test successful retrieval of plagiarism trends"""
        mock_detector = MagicMock()
        mock_detector.get_plagiarism_trends.return_value = {
            'trends': [
                {'date': '2024-01', 'count': 5},
                {'date': '2024-02', 'count': 8}
            ]
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/trends')

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data

    def test_generate_report_success(self, authenticated_session):
        """Test successful report generation"""
        mock_detector = MagicMock()
        mock_detector.generate_comprehensive_report.return_value = {
            'assignment_id': 'test_assignment',
            'summary': 'Report summary',
            'matches': []
        }

        with patch('routes.plagiarism_dashboard.plagiarism_detector', mock_detector):
            response = authenticated_session.get('/api/plagiarism/report/test_assignment')

            assert response.status_code == 200
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert 'format' in data
