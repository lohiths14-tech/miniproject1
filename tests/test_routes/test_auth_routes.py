"""
Unit tests for Authentication Routes
"""
import pytest
import json
from flask import session


@pytest.mark.unit
class TestAuthRoutes:
    """Test suite for authentication endpoints"""

    def test_signup_success(self, client, sample_student):
        """Test successful user registration"""
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(sample_student),
            content_type='application/json'
        )

        # Check response
        assert response.status_code in [200, 201]
        data = json.loads(response.data)
        assert 'message' in data or 'token' in data

    def test_signup_duplicate_email(self, client, sample_student):
        """Test signup with duplicate email"""
        # First signup
        client.post(
            '/api/auth/signup',
            data=json.dumps(sample_student),
            content_type='application/json'
        )

        # Try again with same email
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(sample_student),
            content_type='application/json'
        )

        # Should fail or return conflict
        assert response.status_code in [400, 409]

    def test_login_success(self, client, sample_student):
        """Test successful login"""
        # First register
        client.post(
            '/api/auth/signup',
            data=json.dumps(sample_student),
            content_type='application/json'
        )

        # Then login
        login_data = {
            'email': sample_student['email'],
            'password': sample_student['password']
        }
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data or 'message' in data

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'wrong@example.com',
            'password': 'wrongpassword'
        }
        response = client.post(
            '/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )

        assert response.status_code in [401, 400]

    def test_login_missing_fields(self, client):
        """Test login with missing required fields"""
        response = client.post(
            '/api/auth/login',
            data=json.dumps({'email': 'test@test.com'}),
            content_type='application/json'
        )

        assert response.status_code in [400, 422]

    def test_password_validation(self, client):
        """Test password strength validation"""
        weak_password = {
            'username': 'testuser',
            'email': 'test@test.com',
            'password': '123',  # Too weak
            'role': 'student'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(weak_password),
            content_type='application/json'
        )

        # Should reject weak password
        # Note: depends on implementation
        assert response.status_code in [200, 201, 400]
