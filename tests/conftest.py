"""
Pytest configuration and shared fixtures for comprehensive testing
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load test environment variables
load_dotenv('.env.test')

from app import create_app
from pymongo import MongoClient
import redis
try:
    import mongomock
    import fakeredis
except ImportError:
    mongomock = None
    fakeredis = None


# Shared database client for mongomock to ensure app and tests see same data
_shared_mongomock_client = None
if mongomock:
    _shared_mongomock_client = mongomock.MongoClient()

@pytest.fixture(scope="session")
def app():
    """Create and configure a test instance of the Flask app"""
    # Set testing flag before creating app to disable Talisman
    os.environ['TESTING'] = 'True'

    if mongomock:
        from flask_pymongo import PyMongo
        # Create a mock PyMongo class that returns a configured instance
        class MockPyMongo(PyMongo):
            def __init__(self, app=None, **kwargs):
                self.cx = _shared_mongomock_client
                self.db = self.cx.get_database('test_ai_grading')
                if app is not None:
                    self.init_app(app)

            def init_app(self, app):
                app.mongo = self

        # Patch PyMongo BEFORE creating app
        with patch('app.PyMongo', MockPyMongo):
            app = create_app()

            app.config.update({
                'TESTING': True,
                'SECRET_KEY': 'test-secret-key',
                'MONGODB_URI': 'mongodb://localhost:27017/ai_grading_test',
                'JWT_SECRET_KEY': 'test-jwt-secret',
                'OPENAI_API_KEY': 'test-api-key',
                'RATELIMIT_ENABLED': False
            })

            # Disable rate limiter if it exists
            if hasattr(app, 'limiter') and app.limiter:
                app.limiter.enabled = False

            yield app
    else:
        app = create_app()

        app.config.update({
            'TESTING': True,
            'SECRET_KEY': 'test-secret-key',
            'MONGODB_URI': 'mongodb://localhost:27017/ai_grading_test',
            'JWT_SECRET_KEY': 'test-jwt-secret',
            'OPENAI_API_KEY': 'test-api-key',
            'RATELIMIT_ENABLED': False
        })

        # Disable rate limiter if it exists
        if hasattr(app, 'limiter') and app.limiter:
            app.limiter.enabled = False

        yield app

    # Cleanup
    if 'TESTING' in os.environ:
        del os.environ['TESTING']


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(app, test_user):
    """Generate test authentication headers with valid JWT"""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=test_user['email'])
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }


@pytest.fixture
def lecturer_headers(app, test_lecturer):
    """Generate test lecturer authentication headers with valid JWT"""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=test_lecturer['email'])
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-User-Role': 'lecturer'
        }


@pytest.fixture
def admin_headers(app, test_admin):
    """Generate test admin authentication headers with valid JWT"""
    from flask_jwt_extended import create_access_token
    with app.app_context():
        token = create_access_token(identity=test_admin['email'], additional_claims={"role": "admin"})
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-User-Role': 'admin'
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


@pytest.fixture(scope="session")
def test_db_client():
    """Create MongoDB test client for the session"""
    if mongomock:
        client = _shared_mongomock_client
    else:
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27018/test_ai_grading'))
    yield client
    if not mongomock:
         client.close()


@pytest.fixture(scope="function")
def test_db(test_db_client):
    """Provide clean test database for each test"""
    db_name = os.getenv('MONGODB_TEST_DB', 'test_ai_grading')
    db = test_db_client[db_name]

    yield db

    # Cleanup: Drop all collections after test
    try:
        for collection_name in db.list_collection_names():
            db[collection_name].drop()
    except Exception:
        # Ignore cleanup errors (e.g., if MongoDB is not running)
        pass


@pytest.fixture(scope="session")
def test_redis_client():
    """Create Redis test client for the session"""
    if fakeredis:
        client = fakeredis.FakeRedis()
    else:
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6380/0')
        client = redis.from_url(redis_url)
    yield client
    client.close()


@pytest.fixture(scope="function")
def test_redis(test_redis_client):
    """Provide clean Redis cache for each test"""
    yield test_redis_client
    # Cleanup: Flush test Redis database
    test_redis_client.flushdb()


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls"""
    with patch('openai.ChatCompletion.create') as mock:
        mock.return_value = Mock(
            choices=[
                Mock(
                    message=Mock(
                        content='{"score": 85, "feedback": "Good code quality", "suggestions": ["Add error handling"]}'
                    )
                )
            ]
        )
        yield mock


@pytest.fixture
def mock_email():
    """Mock email sending"""
    with patch('flask_mail.Mail.send') as mock:
        yield mock


@pytest.fixture
def mock_celery():
    """Mock Celery task execution"""
    with patch('celery.app.task.Task.apply_async') as mock:
        mock.return_value = Mock(id='test-task-id', state='SUCCESS')
        yield mock


@pytest.fixture
def test_user(test_db):
    """Create a test user in the database"""
    from models import User
    user_data = {
        'email': 'testuser@example.com',
        'name': 'Test User',
        'role': 'student',
        'password': 'hashed_password_here',
        'usn': 'TEST001'
    }
    user_id = test_db.users.insert_one(user_data).inserted_id
    user_data['_id'] = user_id
    return user_data


@pytest.fixture
def test_lecturer(test_db):
    """Create a test lecturer in the database"""
    lecturer_data = {
        'email': 'lecturer@example.com',
        'name': 'Test Lecturer',
        'role': 'lecturer',
        'password': 'hashed_password_here'
    }
    lecturer_id = test_db.users.insert_one(lecturer_data).inserted_id
    lecturer_data['_id'] = lecturer_id
    return lecturer_data


@pytest.fixture
def test_admin(test_db):
    """Create a test admin in the database"""
    admin_data = {
        'email': 'admin@example.com',
        'name': 'Test Admin',
        'role': 'admin',
        'password': 'hashed_password_here'
    }
    admin_id = test_db.users.insert_one(admin_data).inserted_id
    admin_data['_id'] = admin_id
    return admin_data


@pytest.fixture
def test_assignment(test_db, test_lecturer):
    """Create a test assignment in the database"""
    from datetime import datetime, timedelta
    assignment_data = {
        'title': 'Test Assignment',
        'description': 'Write a fibonacci function',
        'language': 'python',
        'deadline': datetime.now() + timedelta(days=7),
        'creator_id': test_lecturer['_id'],
        'test_cases': [
            {'input': '5', 'expected_output': '5'},
            {'input': '10', 'expected_output': '55'}
        ],
        'created_at': datetime.now()
    }
    assignment_id = test_db.assignments.insert_one(assignment_data).inserted_id
    assignment_data['_id'] = assignment_id
    return assignment_data


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client"""
    # Login and get JWT token
    response = client.post('/api/auth/login', json={
        'email': test_user['email'],
        'password': 'password123'
    })

    if response.status_code == 200:
        token = response.json.get('token')
        client.environ_base['HTTP_AUTHORIZATION'] = f'Bearer {token}'

    return client


@pytest.fixture(autouse=True)
def reset_test_data():
    """Reset test data before each test"""
    # Clear simple_auth in-memory database before each test
    import simple_auth
    simple_auth.USERS_DB.clear()

    yield

    # Cleanup after test
    simple_auth.USERS_DB.clear()
