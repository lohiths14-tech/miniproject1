# In-memory authentication system with user registration
from passlib.hash import pbkdf2_sha256
from datetime import datetime

# In-memory user storage for testing
USERS_DB = {}

def create_test_users():
    """Initialize test users for development"""
    # Create default lecturer account
    register_user(
        "lecturer@example.com",
        "Test Lecturer",
        "password123",
        "lecturer",
        lecturer_id="LEC001"
    )

    # Create default student account
    register_user(
        "student@example.com",
        "Test Student",
        "password123",
        "student",
        usn="4PM24AI001"
    )

    # Create default admin account
    register_user(
        "admin@example.com",
        "Admin User",
        "admin123",
        "lecturer",
        lecturer_id="ADMIN001"
    )

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    user = USERS_DB.get(email.lower())
    if user and pbkdf2_sha256.verify(password, user['password_hash']):
        return user
    return None

def register_user(email, username, password, role, **kwargs):
    """Register a new user"""
    email = email.lower()
    if email in USERS_DB:
        return None, "User already exists"

    user_data = {
        'email': email,
        'username': username,
        'password_hash': pbkdf2_sha256.hash(password),
        'role': role,
        'created_at': datetime.utcnow(),
        'is_active': True
    }

    if role == 'student':
        user_data['usn'] = kwargs.get('usn', '')
    else:
        user_data['lecturer_id'] = kwargs.get('lecturer_id', '')

    USERS_DB[email] = user_data
    return user_data, None

def get_user_by_email(email):
    """Get user by email"""
    return USERS_DB.get(email.lower())

# Initialize test users
create_test_users()
