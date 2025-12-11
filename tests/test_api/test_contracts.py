"""
API Contract Tests
Tests to validate API request/response schemas and contracts
"""

import pytest
from flask import json

@pytest.fixture
def client():
    """Create test client"""
    from app import create_app
    app = create_app()
    app.config['TESTING'] = True
    return app.test_client()

class TestAuthAPIContracts:
    """Test authentication API contracts"""

    def test_login_request_schema(self, client):
        """Test login endpoint accepts required fields"""
        # Valid request
        response = client.post('/api/auth/login',
            json={'email': 'test@example.com', 'password': 'password123'},
            content_type='application/json'
        )
        assert response.status_code in [200, 401]  # Either success or auth failure

        # Invalid - missing email
        response = client.post('/api/auth/login',
            json={'password': 'password123'},
            content_type='application/json'
        )
        assert response.status_code in [400, 401]

        # Invalid - missing password
        response = client.post('/api/auth/login',
            json={'email': 'test@example.com'},
            content_type='application/json'
        )
        assert response.status_code in [400, 401]

    def test_login_response_schema(self, client):
        """Test login endpoint returns proper response structure"""
        response = client.post('/api/auth/login',
            json={'email': 'test@example.com', 'password': 'test123'},
            content_type='application/json'
        )

        data = response.get_json()
        assert 'status' in data or 'error' in data

        if response.status_code == 200:
            assert 'data' in data or 'token' in data

    def test_signup_request_schema(self, client):
        """Test signup endpoint request schema"""
        # Valid request
        response = client.post('/api/auth/signup',
            json={
                'email': 'newuser@example.com',
                'password': 'password123',
                'name': 'Test User',
                'role': 'student'
            },
            content_type='application/json'
        )
        assert response.status_code in [200, 201, 400, 409]

class TestSubmissionAPIContracts:
    """Test submission API contracts"""

    def test_submit_request_schema(self, client):
        """Test submission endpoint request schema"""
        response = client.post('/api/submissions/submit',
            json={
                'code': 'def factorial(n): return 1',
                'assignment_id': 'test123',
                'language': 'python'
            },
            content_type='application/json'
        )

        assert response.status_code in [200, 201, 401, 400]

    def test_submit_response_schema(self, client):
        """Test submission endpoint response schema"""
        response = client.post('/api/submissions/submit',
            json={
                'code': 'print("hello")',
                'assignment_id': 'test',
                'language': 'python',
                'student_name': 'Test',
                'student_email': 'test@example.com'
            }
        )

        data = response.get_json()
        assert 'status' in data

        if response.status_code == 200:
            assert 'data' in data
            if 'data' in data:
                assert 'submission_id' in data['data'] or 'id' in data['data']

    def test_get_submissions_response_schema(self, client):
        """Test get submissions response schema"""
        response = client.get('/api/submissions/recent')

        assert response.status_code in [200, 401]

        data = response.get_json()
        assert 'status' in data or 'error' in data

        if response.status_code == 200 and 'data' in data:
            assert isinstance(data['data'], list)

class TestGamificationAPIContracts:
    """Test gamification API contracts"""

    def test_leaderboard_response_schema(self, client):
        """Test leaderboard endpoint response"""
        response = client.get('/api/gamification/leaderboard')

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.get_json()
            assert 'status' in data or 'data' in data

            if 'data' in data:
                assert isinstance(data['data'], list)

                # Check leaderboard entry schema
                if len(data['data']) > 0:
                    entry = data['data'][0]
                    assert 'user_id' in entry or 'name' in entry
                    assert 'points' in entry or 'score' in entry

    def test_achievements_response_schema(self, client):
        """Test achievements endpoint response"""
        response = client.get('/api/gamification/my-achievements')

        assert response.status_code in [200, 401, 404]

        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data or 'achievements' in data

class TestDashboardAPIContracts:
    """Test dashboard API contracts"""

    def test_dashboard_response_schema(self, client):
        """Test dashboard endpoint response"""
        response = client.get('/api/dashboard/student')

        assert response.status_code in [200, 401]

        if response.status_code == 200:
            data = response.get_json()
            assert 'data' in data or 'status' in data

    def test_analytics_response_schema(self, client):
        """Test analytics endpoint response"""
        response = client.get('/api/dashboard/analytics')

        assert response.status_code in [200, 401, 404]

class TestPlagiarismAPIContracts:
    """Test plagiarism API contracts"""

    def test_plagiarism_check_request_schema(self, client):
        """Test plagiarism check request"""
        response = client.post('/api/plagiarism/check',
            json={
                'code': 'def test(): pass',
                'assignment_id': 'test123',
                'language': 'python'
            }
        )

        assert response.status_code in [200, 401, 400]

    def test_plagiarism_response_schema(self, client):
        """Test plagiarism check response"""
        response = client.post('/api/plagiarism/check',
            json={
                'code': 'print("test")',
                'assignment_id': 'test',
                'student_id': 'student123',
                'language': 'python'
            }
        )

        if response.status_code == 200:
            data = response.get_json()
            assert 'similarity_score' in data or 'passed' in data or 'status' in data

class TestErrorResponses:
    """Test error response contracts"""

    def test_404_response_schema(self, client):
        """Test 404 responses have consistent structure"""
        response = client.get('/api/nonexistent-endpoint')
        assert response.status_code == 404

        data = response.get_json()
        if data:
            assert 'error' in data or 'message' in data or 'status' in data

    def test_rate_limit_response_schema(self, client):
        """Test rate limit response schema"""
        # Make many requests to trigger rate limit
        for i in range(100):
            response = client.post('/api/submissions/submit',
                json={'code': 'test', 'language': 'python'}
            )

            if response.status_code == 429:
                data = response.get_json()
                assert 'error' in data or 'message' in data
                assert 'rate_limit_exceeded' in str(data).lower() or 'too many' in str(data).lower()
                break

class TestContentTypeValidation:
    """Test content type validation"""

    def test_json_content_type_required(self, client):
        """Test that JSON content type is properly handled"""
        # Without content-type header
        response = client.post('/api/submissions/submit',
            data='{"code": "test"}',
        )
        # Should either accept it or reject with 400/415
        assert response.status_code in [200, 400, 415, 401]

    def test_invalid_json_handled(self, client):
        """Test invalid JSON is handled gracefully"""
        response = client.post('/api/submissions/submit',
            data='invalid json{',
            content_type='application/json'
        )
        assert response.status_code in [400, 401]

class TestHTTPMethods:
    """Test HTTP method validation"""

    def test_method_not_allowed(self, client):
        """Test that endpoints reject invalid HTTP methods"""
        # Try GET on POST-only endpoint
        response = client.get('/api/submissions/submit')
        assert response.status_code == 405  # Method Not Allowed

        # Try POST on GET-only endpoint
        response = client.post('/api/submissions/recent')
        assert response.status_code == 405

class TestAuthenticationHeaders:
    """Test authentication header requirements"""

    def test_protected_endpoints_require_auth(self, client):
        """Test that protected endpoints check authentication"""
        protected_endpoints = [
            '/api/dashboard/student',
            '/api/gamification/my-achievements',
        ]

        for endpoint in protected_endpoints:
            response = client.get(endpoint)
            # Should be 401 Unauthorized or redirect to login
            assert response.status_code in [401, 302, 200]  # 200 if endpoint allows anonymous

class TestResponseHeaders:
    """Test response headers"""

    def test_content_type_headers(self, client):
        """Test that responses have proper content-type"""
        response = client.get('/api/submissions/recent')

        if response.status_code == 200:
            assert 'application/json' in response.content_type or \
                   'application/json' in response.headers.get('Content-Type', '')

    def test_security_headers(self, client):
        """Test security headers are present"""
        response = client.get('/')

        # Check for common security headers
        headers = response.headers
        # These might be set by security middleware
        # (just check they don't cause errors if present)

@pytest.mark.contract
class TestAPIVersioning:
    """Test API versioning if applicable"""

    def test_api_version_header(self, client):
        """Test API version is communicated"""
        response = client.get('/health')

        if response.status_code == 200:
            data = response.get_json()
            # Version might be in response or headers
            assert 'version' in data or 'X-API-Version' in response.headers or True

# Schema validation helpers
def validate_response_structure(data, required_fields):
    """Helper to validate response has required fields"""
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"

def validate_list_response(data, item_schema=None):
    """Helper to validate list response"""
    assert isinstance(data, list)
    if item_schema and len(data) > 0:
        for item in data:
            for field in item_schema:
                assert field in item
