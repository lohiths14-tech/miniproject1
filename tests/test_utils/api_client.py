"""
Test API client for making requests to the application
"""
import json
from typing import Dict, Any, Optional


class TestAPIClient:
    """
    Test client wrapper for making API requests with authentication
    """

    def __init__(self, client, token=None):
        """
        Initialize test API client

        Args:
            client: Flask test client
            token: JWT authentication token (optional)
        """
        self.client = client
        self.token = token
        self.last_response = None

    def set_token(self, token):
        """Set authentication token"""
        self.token = token

    def clear_token(self):
        """Clear authentication token"""
        self.token = None

    def _get_headers(self, headers=None):
        """Get headers with authentication"""
        default_headers = {'Content-Type': 'application/json'}

        if self.token:
            default_headers['Authorization'] = f'Bearer {self.token}'

        if headers:
            default_headers.update(headers)

        return default_headers

    def get(self, url, headers=None, **kwargs):
        """Make GET request"""
        self.last_response = self.client.get(
            url,
            headers=self._get_headers(headers),
            **kwargs
        )
        return self.last_response

    def post(self, url, data=None, json_data=None, headers=None, **kwargs):
        """Make POST request"""
        if json_data:
            self.last_response = self.client.post(
                url,
                data=json.dumps(json_data),
                headers=self._get_headers(headers),
                **kwargs
            )
        else:
            self.last_response = self.client.post(
                url,
                data=data,
                headers=self._get_headers(headers),
                **kwargs
            )
        return self.last_response

    def put(self, url, data=None, json_data=None, headers=None, **kwargs):
        """Make PUT request"""
        if json_data:
            self.last_response = self.client.put(
                url,
                data=json.dumps(json_data),
                headers=self._get_headers(headers),
                **kwargs
            )
        else:
            self.last_response = self.client.put(
                url,
                data=data,
                headers=self._get_headers(headers),
                **kwargs
            )
        return self.last_response

    def patch(self, url, data=None, json_data=None, headers=None, **kwargs):
        """Make PATCH request"""
        if json_data:
            self.last_response = self.client.patch(
                url,
                data=json.dumps(json_data),
                headers=self._get_headers(headers),
                **kwargs
            )
        else:
            self.last_response = self.client.patch(
                url,
                data=data,
                headers=self._get_headers(headers),
                **kwargs
            )
        return self.last_response

    def delete(self, url, headers=None, **kwargs):
        """Make DELETE request"""
        self.last_response = self.client.delete(
            url,
            headers=self._get_headers(headers),
            **kwargs
        )
        return self.last_response

    def login(self, email, password):
        """
        Login and set authentication token

        Args:
            email: User email
            password: User password

        Returns:
            Response object
        """
        response = self.post('/api/auth/login', json_data={
            'email': email,
            'password': password
        })

        if response.status_code == 200:
            data = response.get_json()
            if 'token' in data:
                self.set_token(data['token'])

        return response

    def logout(self):
        """Logout and clear token"""
        response = self.post('/api/auth/logout')
        self.clear_token()
        return response

    def signup(self, email, password, name, role='student', **kwargs):
        """
        Sign up a new user

        Args:
            email: User email
            password: User password
            name: User name
            role: User role (student/lecturer)
            **kwargs: Additional user data

        Returns:
            Response object
        """
        data = {
            'email': email,
            'password': password,
            'name': name,
            'role': role,
            **kwargs
        }
        return self.post('/api/auth/signup', json_data=data)

    def get_json(self):
        """Get JSON from last response"""
        if self.last_response:
            return self.last_response.get_json()
        return None

    def assert_success(self, status_code=200):
        """Assert last response was successful"""
        assert self.last_response is not None, "No response to check"
        assert self.last_response.status_code == status_code, \
            f"Expected {status_code}, got {self.last_response.status_code}"

    def assert_error(self, status_code=400):
        """Assert last response was an error"""
        assert self.last_response is not None, "No response to check"
        assert self.last_response.status_code == status_code, \
            f"Expected {status_code}, got {self.last_response.status_code}"

    def assert_unauthorized(self):
        """Assert last response was unauthorized"""
        self.assert_error(401)

    def assert_forbidden(self):
        """Assert last response was forbidden"""
        self.assert_error(403)

    def assert_not_found(self):
        """Assert last response was not found"""
        self.assert_error(404)


class AuthenticatedAPIClient(TestAPIClient):
    """
    API client that automatically handles authentication
    """

    def __init__(self, client, user_email='test@example.com', user_password='password123'):
        """
        Initialize authenticated API client

        Args:
            client: Flask test client
            user_email: Email for authentication
            user_password: Password for authentication
        """
        super().__init__(client)
        self.user_email = user_email
        self.user_password = user_password
        self._authenticate()

    def _authenticate(self):
        """Authenticate and get token"""
        response = self.login(self.user_email, self.user_password)
        if response.status_code != 200:
            # If login fails, try to sign up first
            self.signup(
                self.user_email,
                self.user_password,
                'Test User',
                'student'
            )
            self.login(self.user_email, self.user_password)


# Helper functions

def create_test_client(app, authenticated=False, **auth_kwargs):
    """
    Create a test API client

    Args:
        app: Flask application
        authenticated: Whether to create authenticated client
        **auth_kwargs: Arguments for authentication

    Returns:
        TestAPIClient or AuthenticatedAPIClient
    """
    client = app.test_client()

    if authenticated:
        return AuthenticatedAPIClient(client, **auth_kwargs)

    return TestAPIClient(client)


def make_request(client, method, url, **kwargs):
    """
    Make a request using the test client

    Args:
        client: Test client
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        **kwargs: Additional request arguments

    Returns:
        Response object
    """
    method = method.upper()

    if method == 'GET':
        return client.get(url, **kwargs)
    elif method == 'POST':
        return client.post(url, **kwargs)
    elif method == 'PUT':
        return client.put(url, **kwargs)
    elif method == 'PATCH':
        return client.patch(url, **kwargs)
    elif method == 'DELETE':
        return client.delete(url, **kwargs)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")
