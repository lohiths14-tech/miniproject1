"""
Comprehensive API Tests for Gamification Endpoints (Task 20)
Tests for /api/gamification/* endpoints
"""

import pytest
from unittest.mock import patch, MagicMock


# ==================== 20.1 Test Gamification API Endpoints ====================

class TestGamificationAPI:
    """Test suite for Gamification API endpoints (Task 20.1)"""

    def test_get_leaderboard_success(self, client):
        """Test GET /api/gamification/leaderboard - successful retrieval"""
        response = client.get('/api/gamification/leaderboard')

        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'leaderboard' in data['data']
        assert 'timeframe' in data['data']
        assert 'generated_at' in data['data']

    def test_get_leaderboard_with_timeframe(self, client):
        """Test GET /api/gamification/leaderboard with timeframe filter"""
        response = client.get('/api/gamification/leaderboard?timeframe=weekly')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['timeframe'] == 'weekly'

    def test_get_leaderboard_with_course_filter(self, client):
        """Test GET /api/gamification/leaderboard with course_id filter"""
        response = client.get('/api/gamification/leaderboard?course_id=CS101')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'leaderboard' in data['data']

    def test_get_leaderboard_monthly_timeframe(self, client):
        """Test GET /api/gamification/leaderboard with monthly timeframe"""
        response = client.get('/api/gamification/leaderboard?timeframe=monthly')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert data['data']['timeframe'] == 'monthly'

    def test_get_user_stats_success(self, client):
        """Test GET /api/gamification/user/stats - get user gamification stats"""
        response = client.get('/api/gamification/user/stats')

        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'success'
        assert 'data' in data
        # Should contain achievement summary and level info
        assert 'total_points' in data['data'] or 'level_info' in data['data']

    def test_get_all_badges_success(self, client):
        """Test GET /api/gamification/badges - get all available badges"""
        response = client.get('/api/gamification/badges')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'badges' in data['data']
        assert 'challenges' in data['data']
        assert isinstance(data['data']['badges'], dict)
        assert isinstance(data['data']['challenges'], dict)

    def test_get_monthly_challenges_success(self, client):
        """Test GET /api/gamification/challenges/monthly - get current challenges"""
        response = client.get('/api/gamification/challenges/monthly')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'challenges' in data['data']
        assert 'month' in data['data']

    def test_award_points_success(self, client):
        """Test POST /api/gamification/award-points - award points for action"""
        response = client.post('/api/gamification/award-points',
            json={
                'user_id': 'test_user_123',
                'action': 'submission',
                'metadata': {'score': 85}
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data

    def test_award_points_missing_user_id(self, client):
        """Test POST /api/gamification/award-points - missing user_id returns 400"""
        response = client.post('/api/gamification/award-points',
            json={
                'action': 'submission'
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'user_id' in data['message'].lower()

    def test_award_points_missing_action(self, client):
        """Test POST /api/gamification/award-points - missing action returns 400"""
        response = client.post('/api/gamification/award-points',
            json={
                'user_id': 'test_user_123'
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'action' in data['message'].lower()

    def test_award_points_with_metadata(self, client):
        """Test POST /api/gamification/award-points - with optional metadata"""
        response = client.post('/api/gamification/award-points',
            json={
                'user_id': 'test_user_123',
                'action': 'perfect_score',
                'metadata': {
                    'assignment_id': 'assign_001',
                    'score': 100,
                    'time_taken': 300
                }
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_check_achievements_success(self, client):
        """Test POST /api/gamification/check-achievements - check for new achievements"""
        response = client.post('/api/gamification/check-achievements',
            json={
                'user_id': 'test_user_123',
                'user_stats': {
                    'total_submissions': 10,
                    'perfect_scores': 3,
                    'streak_days': 7
                }
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'new_badges' in data['data']

    def test_check_achievements_missing_user_id(self, client):
        """Test POST /api/gamification/check-achievements - missing user_id returns 400"""
        response = client.post('/api/gamification/check-achievements',
            json={
                'user_stats': {}
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'
        assert 'user_id' in data['message'].lower()

    def test_update_streak_success(self, client):
        """Test POST /api/gamification/streak/update - update user streak"""
        response = client.post('/api/gamification/streak/update',
            json={
                'user_id': 'test_user_123',
                'last_submission_date': '2025-11-30T10:00:00Z'
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data

    def test_update_streak_missing_user_id(self, client):
        """Test POST /api/gamification/streak/update - missing user_id returns 400"""
        response = client.post('/api/gamification/streak/update',
            json={
                'last_submission_date': '2025-11-30T10:00:00Z'
            }
        )

        assert response.status_code == 400
        data = response.get_json()
        assert data['status'] == 'error'

    def test_calculate_level_success(self, client):
        """Test POST /api/gamification/level/calculate - calculate level from points"""
        response = client.post('/api/gamification/level/calculate',
            json={
                'total_points': 1500
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        # Should contain level information
        assert 'level' in data['data'] or 'current_level' in data['data']

    def test_calculate_level_zero_points(self, client):
        """Test POST /api/gamification/level/calculate - with zero points"""
        response = client.post('/api/gamification/level/calculate',
            json={
                'total_points': 0
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'

    def test_demo_student_profile_success(self, client):
        """Test GET /api/gamification/demo/student-profile - demo profile"""
        response = client.get('/api/gamification/demo/student-profile')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'user_info' in data['data']
        assert 'stats' in data['data']
        assert 'level' in data['data']

    def test_demo_award_submission_success(self, client):
        """Test POST /api/gamification/demo/award-submission - demo award"""
        response = client.post('/api/gamification/demo/award-submission',
            json={
                'score': 95,
                'time_taken': 450
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'data' in data
        assert 'submission_award' in data['data']
        assert 'total_points_earned' in data['data']

    def test_demo_award_submission_speed_bonus(self, client):
        """Test POST /api/gamification/demo/award-submission - with speed bonus"""
        response = client.post('/api/gamification/demo/award-submission',
            json={
                'score': 100,
                'time_taken': 250  # Fast completion
            }
        )

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        # Should include speed bonus for fast completion
        assert 'speed_bonus' in data['data']

    def test_response_schema_validation_leaderboard(self, client):
        """Test response schema validation for leaderboard endpoint"""
        response = client.get('/api/gamification/leaderboard')

        assert response.status_code == 200
        data = response.get_json()

        # Validate response structure
        assert isinstance(data, dict)
        assert 'status' in data
        assert 'data' in data
        assert isinstance(data['data'], dict)
        assert 'leaderboard' in data['data']
        assert isinstance(data['data']['leaderboard'], list)

    def test_response_schema_validation_badges(self, client):
        """Test response schema validation for badges endpoint"""
        response = client.get('/api/gamification/badges')

        assert response.status_code == 200
        data = response.get_json()

        # Validate response structure
        assert isinstance(data, dict)
        assert 'status' in data
        assert data['status'] == 'success'
        assert 'data' in data
        assert isinstance(data['data'], dict)
        assert 'badges' in data['data']
        assert 'challenges' in data['data']

    def test_response_schema_validation_award_points(self, client):
        """Test response schema validation for award-points endpoint"""
        response = client.post('/api/gamification/award-points',
            json={
                'user_id': 'test_user',
                'action': 'submission'
            }
        )

        assert response.status_code == 200
        data = response.get_json()

        # Validate response structure
        assert isinstance(data, dict)
        assert 'status' in data
        assert data['status'] == 'success'
        assert 'data' in data

    def test_error_handling_invalid_json(self, client):
        """Test error handling for invalid JSON in POST requests"""
        response = client.post('/api/gamification/award-points',
            data='invalid json',
            content_type='application/json'
        )

        # Should handle invalid JSON gracefully
        assert response.status_code in [400, 500]

    def test_leaderboard_empty_result(self, client):
        """Test leaderboard returns empty list when no data"""
        # This tests that the endpoint handles empty data gracefully
        response = client.get('/api/gamification/leaderboard?course_id=nonexistent')

        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
        assert 'leaderboard' in data['data']
        assert isinstance(data['data']['leaderboard'], list)

    def test_award_points_different_actions(self, client):
        """Test awarding points for different action types"""
        actions = ['submission', 'perfect_score', 'speed_demon', 'first_submission']

        for action in actions:
            response = client.post('/api/gamification/award-points',
                json={
                    'user_id': f'test_user_{action}',
                    'action': action
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'

    def test_concurrent_point_awards(self, client):
        """Test multiple point awards for same user"""
        user_id = 'test_concurrent_user'

        # Award points multiple times
        for i in range(3):
            response = client.post('/api/gamification/award-points',
                json={
                    'user_id': user_id,
                    'action': 'submission',
                    'metadata': {'submission_number': i + 1}
                }
            )

            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'success'
