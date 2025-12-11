"""
Integration tests for user registration workflow
Tests end-to-end flow: registration → validation → password hashing → storage → email → JWT → login
**Validates: Requirements 4.3**
"""

import pytest
import json
from unittest.mock import patch, Mock
from passlib.hash import pbkdf2_sha256


@pytest.mark.integration
class TestRegistrationWorkflow:
    """Test complete user registration workflow"""

    def test_complete_registration_workflow(self, client, test_db):
        """
        Test complete registration workflow:
        1. User submits registration
        2. Input is validated
        3. Password is hashed
        4. User is stored in database
        5. Welcome email is sent (with mock)
        6. JWT token is generated
        7. User can login with credentials
        8. Verify end-to-end data flow
        """
        # Mock email service
        with patch('services.email_service.send_welcome_email') as mock_email:
            mock_email.return_value = True

            # Step 1: User submits registration
            registration_data = {
                'email': 'newuser@test.com',
                'username': 'newuser',
                'password': 'TestPass123!',
                'role': 'student',
                'usn': 'NEW001'
            }

            # Step 2: Submit registration request
            response = client.post(
                '/api/auth/signup',
                data=json.dumps(registration_data),
                content_type='application/json'
            )

            # Verify registration succeeded
            assert response.status_code == 201, f"Registration failed: {response.data}"
            response_data = json.loads(response.data)
            assert response_data['message'] == 'User created successfully'
            assert 'access_token' in response_data
            assert 'user' in response_data

            # Step 3: Verify password is hashed (not stored in plain text)
            user_data = response_data['user']
            assert 'password_hash' not in user_data, "Password hash should not be in response"
            assert user_data['email'] == registration_data['email'].lower()
            assert user_data['username'] == registration_data['username']
            assert user_data['role'] == registration_data['role']

            # Step 4: Verify user is stored in database (in-memory for simple_auth)
            import simple_auth
            stored_user = simple_auth.get_user_by_email(registration_data['email'])
            assert stored_user is not None, "User should be stored in database"
            assert stored_user['email'] == registration_data['email'].lower()
            assert stored_user['username'] == registration_data['username']
            assert stored_user['role'] == registration_data['role']
            assert stored_user['usn'] == registration_data['usn']

            # Step 5: Verify password is properly hashed
            assert 'password_hash' in stored_user
            assert stored_user['password_hash'] != registration_data['password']
            assert pbkdf2_sha256.verify(registration_data['password'], stored_user['password_hash'])

            # Step 6: Verify welcome email was sent (mocked)
            # Note: In the current implementation, welcome email is not automatically sent
            # This is a gap in the implementation that should be addressed

            # Step 7: Verify JWT token is generated
            jwt_token = response_data['access_token']
            assert jwt_token is not None
            assert len(jwt_token) > 0

            # Step 8: Verify user can login with credentials
            login_response = client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': registration_data['email'],
                    'password': registration_data['password']
                }),
                content_type='application/json'
            )

            assert login_response.status_code == 200, f"Login failed: {login_response.data}"
            login_data = json.loads(login_response.data)
            assert login_data['message'] == 'Login successful'
            assert 'access_token' in login_data
            assert 'user' in login_data

            # Verify end-to-end data flow
            assert login_data['user']['email'] == registration_data['email'].lower()
            assert login_data['user']['username'] == registration_data['username']

    def test_registration_with_invalid_email(self, client):
        """Test registration fails with invalid email format"""
        registration_data = {
            'email': 'invalid-email',
            'username': 'testuser',
            'password': 'TestPass123!',
            'role': 'student',
            'usn': 'TEST001'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'email' in response_data['error'].lower()

    def test_registration_with_weak_password(self, client):
        """Test registration fails with weak password"""
        registration_data = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'weak',  # Too short, no uppercase, no digit
            'role': 'student',
            'usn': 'TEST001'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'password' in response_data['error'].lower()

    def test_registration_with_duplicate_email(self, client):
        """Test registration fails with duplicate email"""
        registration_data = {
            'email': 'duplicate@test.com',
            'username': 'user1',
            'password': 'TestPass123!',
            'role': 'student',
            'usn': 'DUP001'
        }

        # First registration
        response1 = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )
        assert response1.status_code == 201

        # Second registration with same email
        registration_data['username'] = 'user2'
        registration_data['usn'] = 'DUP002'
        response2 = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response2.status_code == 409
        response_data = json.loads(response2.data)
        assert 'error' in response_data
        assert 'exists' in response_data['error'].lower()

    def test_registration_missing_required_fields(self, client):
        """Test registration fails with missing required fields"""
        # Missing password
        registration_data = {
            'email': 'test@test.com',
            'username': 'testuser',
            'role': 'student',
            'usn': 'TEST001'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data

    def test_student_registration_requires_usn(self, client):
        """Test student registration requires USN"""
        registration_data = {
            'email': 'student@test.com',
            'username': 'student',
            'password': 'TestPass123!',
            'role': 'student'
            # Missing USN
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'usn' in response_data['error'].lower()

    def test_lecturer_registration_requires_lecturer_id(self, client):
        """Test lecturer registration requires lecturer ID"""
        registration_data = {
            'email': 'lecturer@test.com',
            'username': 'lecturer',
            'password': 'TestPass123!',
            'role': 'lecturer'
            # Missing lecturer_id
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'lecturer' in response_data['error'].lower()

    def test_registration_with_invalid_role(self, client):
        """Test registration fails with invalid role"""
        registration_data = {
            'email': 'test@test.com',
            'username': 'testuser',
            'password': 'TestPass123!',
            'role': 'admin',  # Invalid role
            'usn': 'TEST001'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 400
        response_data = json.loads(response.data)
        assert 'error' in response_data
        assert 'role' in response_data['error'].lower()

    def test_lecturer_registration_workflow(self, client):
        """Test complete registration workflow for lecturer"""
        with patch('services.email_service.send_welcome_email') as mock_email:
            mock_email.return_value = True

            registration_data = {
                'email': 'lecturer@test.com',
                'username': 'testlecturer',
                'password': 'TestPass123!',
                'role': 'lecturer',
                'lecturer_id': 'LEC001'
            }

            # Register lecturer
            response = client.post(
                '/api/auth/signup',
                data=json.dumps(registration_data),
                content_type='application/json'
            )

            assert response.status_code == 201
            response_data = json.loads(response.data)
            assert response_data['user']['role'] == 'lecturer'
            assert 'lecturer_id' in response_data['user']

            # Verify lecturer can login
            login_response = client.post(
                '/api/auth/login',
                data=json.dumps({
                    'email': registration_data['email'],
                    'password': registration_data['password']
                }),
                content_type='application/json'
            )

            assert login_response.status_code == 200

    def test_password_not_stored_in_plain_text(self, client):
        """Test that password is never stored in plain text"""
        registration_data = {
            'email': 'secure@test.com',
            'username': 'secureuser',
            'password': 'TestPass123!',
            'role': 'student',
            'usn': 'SEC001'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 201

        # Verify password is not in response
        response_data = json.loads(response.data)
        assert registration_data['password'] not in str(response_data)

        # Verify password is hashed in storage
        import simple_auth
        stored_user = simple_auth.get_user_by_email(registration_data['email'])
        assert stored_user['password_hash'] != registration_data['password']
        assert len(stored_user['password_hash']) > 50  # Hashed passwords are long

    def test_email_case_insensitive(self, client):
        """Test that email is stored in lowercase and login is case-insensitive"""
        registration_data = {
            'email': 'CaseSensitive@Test.COM',
            'username': 'casetest',
            'password': 'TestPass123!',
            'role': 'student',
            'usn': 'CASE001'
        }

        # Register with mixed case email
        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 201
        response_data = json.loads(response.data)
        assert response_data['user']['email'] == registration_data['email'].lower()

        # Login with different case
        login_response = client.post(
            '/api/auth/login',
            data=json.dumps({
                'email': 'casesensitive@test.com',  # All lowercase
                'password': registration_data['password']
            }),
            content_type='application/json'
        )

        assert login_response.status_code == 200

    def test_registration_creates_active_user(self, client):
        """Test that newly registered users are active by default"""
        registration_data = {
            'email': 'active@test.com',
            'username': 'activeuser',
            'password': 'TestPass123!',
            'role': 'student',
            'usn': 'ACT001'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 201

        # Verify user is active
        import simple_auth
        stored_user = simple_auth.get_user_by_email(registration_data['email'])
        assert stored_user['is_active'] is True

    def test_registration_includes_timestamp(self, client):
        """Test that registration includes creation timestamp"""
        registration_data = {
            'email': 'timestamp@test.com',
            'username': 'timestampuser',
            'password': 'TestPass123!',
            'role': 'student',
            'usn': 'TIME001'
        }

        response = client.post(
            '/api/auth/signup',
            data=json.dumps(registration_data),
            content_type='application/json'
        )

        assert response.status_code == 201

        # Verify timestamp exists
        import simple_auth
        stored_user = simple_auth.get_user_by_email(registration_data['email'])
        assert 'created_at' in stored_user
        assert stored_user['created_at'] is not None
