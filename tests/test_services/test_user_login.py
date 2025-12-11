"""
Comprehensive unit tests for user login functionality

This module tests all aspects of user login including:
- Successful login with correct credentials
- Login failures with incorrect password
- Login failures with non-existent user
- JWT token generation and validation
- Token expiration
- Edge cases and error handling

Coverage Target: 95%+ for authentication service
Requirements: 2.4
"""
import pytest
from datetime import datetime, timedelta
from tests.test_utils.assertions import assert_valid_jwt


class TestUserLogin:
    """Test user login functionality - Requirements 2.4"""

    def test_successful_login_with_correct_credentials(self, client):
        """Test successful login with correct credentials"""
        # Arrange - First register a user
        register_data = {
            'email': 'logintest@test.com',
            'username': 'loginuser',
            'password': 'TestPass123',
            'role': 'student',
            'usn': 'LOGIN001'
        }
        client.post('/api/auth/signup', json=register_data)

        login_data = {
            'email': 'logintest@test.com',
            'password': 'TestPass123'
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert 'message' in data
        assert data['message'] == 'Login successful'
        assert data['user']['email'] == 'logintest@test.com'
        assert 'password_hash' not in data['user']  # Password should not be in response

    def test_login_with_incorrect_password(self, client):
        """Test login fails with incorrect password"""
        # Arrange - First register a user
        register_data = {
            'email': 'wrongpass@test.com',
            'username': 'wrongpassuser',
            'password': 'CorrectPass123',
            'role': 'student',
            'usn': 'WRONG001'
        }
        client.post('/api/auth/signup', json=register_data)

        login_data = {
            'email': 'wrongpass@test.com',
            'password': 'WrongPassword123'
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid email or password' in data['error']

    def test_login_with_nonexistent_user(self, client):
        """Test login fails with non-existent user"""
        # Arrange
        login_data = {
            'email': 'nonexistent@test.com',
            'password': 'password123'
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'Invalid email or password' in data['error']

    def test_jwt_token_generation(self, client):
        """Test JWT token is generated correctly"""
        # Arrange - Register and login
        register_data = {
            'email': 'jwttest@test.com',
            'username': 'jwtuser',
            'password': 'JwtPass123',
            'role': 'lecturer',
            'lecturer_id': 'JWT001'
        }
        client.post('/api/auth/signup', json=register_data)

        login_data = {
            'email': 'jwttest@test.com',
            'password': 'JwtPass123'
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        data = response.get_json()
        assert 'access_token' in data
        token = data['access_token']

        # Verify token is valid JWT
        decoded = assert_valid_jwt(token)
        assert 'sub' in decoded or 'identity' in decoded

        # Verify token contains user email
        user_identity = decoded.get('sub') or decoded.get('identity')
        assert user_identity == 'jwttest@test.com'

    def test_token_expiration(self, client):
        """Test JWT token has expiration set"""
        # Arrange - Register and login
        register_data = {
            'email': 'exptest@test.com',
            'username': 'expuser',
            'password': 'ExpPass123',
            'role': 'student',
            'usn': 'EXP001'
        }
        client.post('/api/auth/signup', json=register_data)

        login_data = {
            'email': 'exptest@test.com',
            'password': 'ExpPass123'
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        data = response.get_json()
        token = data['access_token']
        decoded = assert_valid_jwt(token)

        # Verify expiration is set
        assert 'exp' in decoded

        # Verify expiration is in the future
        exp_time = datetime.fromtimestamp(decoded['exp'])
        assert exp_time > datetime.now()

        # Verify expiration is reasonable (not too far in future, not too soon)
        time_until_expiry = exp_time - datetime.now()
        assert timedelta(minutes=1) < time_until_expiry < timedelta(days=365)

    def test_login_missing_email(self, client):
        """Test login fails when email is missing"""
        # Arrange
        login_data = {
            'password': 'TestPass123'
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Email and password are required' in data['error']

    def test_login_missing_password(self, client):
        """Test login fails when password is missing"""
        # Arrange
        login_data = {
            'email': 'test@test.com'
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'Email and password are required' in data['error']

    def test_login_empty_credentials(self, client):
        """Test login fails with empty credentials"""
        # Arrange
        login_data = {
            'email': '',
            'password': ''
        }

        # Act
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_login_case_insensitive_email(self, client):
        """Test login works with different email case"""
        # Arrange - Register with lowercase email
        register_data = {
            'email': 'casetest@test.com',
            'username': 'caseuser',
            'password': 'CasePass123',
            'role': 'student',
            'usn': 'CASE001'
        }
        client.post('/api/auth/signup', json=register_data)

        # Act - Login with uppercase email
        login_data = {
            'email': 'CASETEST@TEST.COM',
            'password': 'CasePass123'
        }
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_login_with_whitespace_in_email(self, client):
        """Test login handles whitespace in email"""
        # Arrange - Register user
        register_data = {
            'email': 'spacetest@test.com',
            'username': 'spaceuser',
            'password': 'SpacePass123',
            'role': 'student',
            'usn': 'SPACE001'
        }
        client.post('/api/auth/signup', json=register_data)

        # Act - Login with whitespace
        login_data = {
            'email': '  spacetest@test.com  ',
            'password': 'SpacePass123'
        }
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_login_returns_user_data(self, client):
        """Test login returns complete user data"""
        # Arrange - Register user
        register_data = {
            'email': 'userdata@test.com',
            'username': 'userdatauser',
            'password': 'UserData123',
            'role': 'lecturer',
            'lecturer_id': 'UD001'
        }
        client.post('/api/auth/signup', json=register_data)

        # Act
        login_data = {
            'email': 'userdata@test.com',
            'password': 'UserData123'
        }
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        data = response.get_json()
        assert 'user' in data
        user = data['user']
        assert user['email'] == 'userdata@test.com'
        assert user['username'] == 'userdatauser'
        assert user['role'] == 'lecturer'
        assert user['lecturer_id'] == 'UD001'
        assert 'password_hash' not in user
        assert 'otp_secret' not in user

    def test_login_deactivated_account(self, client):
        """Test login fails for deactivated account"""
        # Arrange - Register user
        register_data = {
            'email': 'deactivated@test.com',
            'username': 'deactivateduser',
            'password': 'Deactivated123',
            'role': 'student',
            'usn': 'DEACT001'
        }
        client.post('/api/auth/signup', json=register_data)

        # Deactivate the account
        import simple_auth
        user = simple_auth.get_user_by_email('deactivated@test.com')
        user['is_active'] = False

        # Act
        login_data = {
            'email': 'deactivated@test.com',
            'password': 'Deactivated123'
        }
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
        assert 'deactivated' in data['error'].lower()

    def test_login_with_null_json(self, client):
        """Test login handles null JSON gracefully"""
        # Act
        response = client.post('/api/auth/login', json=None)

        # Assert
        # Flask returns 415 (Unsupported Media Type) for null JSON
        assert response.status_code == 415

    def test_login_student_account(self, client):
        """Test login works for student accounts"""
        # Arrange
        register_data = {
            'email': 'student@test.com',
            'username': 'studentuser',
            'password': 'Student123',
            'role': 'student',
            'usn': 'STU123'
        }
        client.post('/api/auth/signup', json=register_data)

        # Act
        login_data = {
            'email': 'student@test.com',
            'password': 'Student123'
        }
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'student'
        assert 'usn' in data['user']

    def test_login_lecturer_account(self, client):
        """Test login works for lecturer accounts"""
        # Arrange
        register_data = {
            'email': 'lecturer@test.com',
            'username': 'lectureruser',
            'password': 'Lecturer123',
            'role': 'lecturer',
            'lecturer_id': 'LEC123'
        }
        client.post('/api/auth/signup', json=register_data)

        # Act
        login_data = {
            'email': 'lecturer@test.com',
            'password': 'Lecturer123'
        }
        response = client.post('/api/auth/login', json=login_data)

        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['role'] == 'lecturer'
        assert 'lecturer_id' in data['user']
