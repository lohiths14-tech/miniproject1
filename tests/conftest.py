"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def app():
    """Create and configure a test instance of the Flask app"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SECRET_KEY': 'test-secret-key',
        'MONGODB_URI': 'mongodb://localhost:27017/ai_grading_test',
        'JWT_SECRET_KEY': 'test-jwt-secret',
        'OPENAI_API_KEY': 'test-api-key'
    })

    yield app


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers():
    """Generate test authentication headers"""
    return {
        'Authorization': 'Bearer test-token',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def sample_code():
    """Sample Python code for testing"""
    return """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

result = fibonacci(5)
print(result)
"""


@pytest.fixture
def sample_test_cases():
    """Sample test cases for code grading"""
    return [
        {
            'input': '5',
            'expected_output': '5'
        },
        {
            'input': '10',
            'expected_output': '55'
        }
    ]


@pytest.fixture
def sample_assignment():
    """Sample assignment data"""
    return {
        'title': 'Test Assignment',
        'description': 'Write a fibonacci function',
        'programming_language': 'python',
        'due_date': '2025-12-31',
        'test_cases': [
            {'input': '5', 'expected_output': '5'},
            {'input': '10', 'expected_output': '55'}
        ]
    }


@pytest.fixture
def sample_student():
    """Sample student user data"""
    return {
        'username': 'test_student',
        'email': 'student@test.com',
        'password': 'TestPassword123!',
        'role': 'student',
        'usn': 'STU001'
    }


@pytest.fixture
def sample_lecturer():
    """Sample lecturer user data"""
    return {
        'username': 'test_lecturer',
        'email': 'lecturer@test.com',
        'password': 'TestPassword123!',
        'role': 'lecturer'
    }


@pytest.fixture(autouse=True)
def reset_test_data():
    """Reset test data before each test"""
    # This will be implemented when we connect to actual database
    # For now, it's a placeholder for in-memory data reset
    yield
    # Cleanup after test
