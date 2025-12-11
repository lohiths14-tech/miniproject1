"""
API v1 Authentication Blueprint

Wraps existing authentication functionality with v1 versioned endpoints.
Maintains backward compatibility with existing clients.
"""

import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

auth_v1_bp = Blueprint('auth_v1', __name__, url_prefix='/api/v1/auth')


def validate_email(email):
    """Validate email format."""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """Validate password strength - at least 8 chars, uppercase, lowercase, digit."""
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


def _add_version_metadata(response_data):
    """Add v1 version metadata to response."""
    response_data['api_version'] = '1.0.0'
    response_data['version'] = 'v1'
    return response_data


@auth_v1_bp.route('/signup', methods=['POST'])
def signup_v1():
    """User signup endpoint - v1."""
    try:
        from models import User
        from services.email_service import send_welcome_email

        data = request.get_json()

        # Validate required fields
        required_fields = ['email', 'username', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(_add_version_metadata({'error': f'{field} is required'})), 400

        email = data['email'].lower().strip()
        username = data['username'].strip()
        password = data['password']
        role = data['role'].lower()

        # Validate email format
        if not validate_email(email):
            return jsonify(_add_version_metadata({'error': 'Invalid email format'})), 400

        # Validate password strength
        if not validate_password(password):
            return jsonify(_add_version_metadata({
                'error': 'Password must be at least 8 characters with uppercase, lowercase, and digit'
            })), 400

        # Validate role
        if role not in ['student', 'lecturer']:
            return jsonify(_add_version_metadata({'error': 'Role must be either student or lecturer'})), 400

        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify(_add_version_metadata({'error': 'User with this email already exists'})), 409

        # Role-specific validation
        if role == 'student':
            if 'usn' not in data or not data['usn']:
                return jsonify(_add_version_metadata({'error': 'USN is required for students'})), 400
            user = User(email, username, password, role, usn=data['usn'])
        else:
            if 'lecturer_id' not in data or not data['lecturer_id']:
                return jsonify(_add_version_metadata({'error': 'Lecturer ID is required for lecturers'})), 400
            user = User(email, username, password, role, lecturer_id=data['lecturer_id'])

        user.save()

        # Send welcome email
        try:
            send_welcome_email(email, username, role)
        except Exception as e:
            print(f'Failed to send welcome email: {str(e)}')

        access_token = create_access_token(identity=str(user._id))

        return jsonify(_add_version_metadata({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict(),
        })), 201

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Registration failed: {str(e)}'})), 500


@auth_v1_bp.route('/login', methods=['POST'])
def login_v1():
    """User login endpoint - v1."""
    try:
        from models import User

        data = request.get_json()

        if not data.get('email') or not data.get('password'):
            return jsonify(_add_version_metadata({'error': 'Email and password are required'})), 400

        email = data['email'].lower().strip()
        password = data['password']

        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            return jsonify(_add_version_metadata({'error': 'Invalid email or password'})), 401

        if not user.is_active:
            return jsonify(_add_version_metadata({'error': 'Account is deactivated'})), 401

        access_token = create_access_token(identity=str(user._id))

        return jsonify(_add_version_metadata({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict(),
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Login failed: {str(e)}'})), 500


@auth_v1_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile_v1():
    """Get user profile endpoint - v1."""
    try:
        from models import User

        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)

        if not user:
            return jsonify(_add_version_metadata({'error': 'User not found'})), 404

        return jsonify(_add_version_metadata({'user': user.to_dict()})), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to get profile: {str(e)}'})), 500


@auth_v1_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout_v1():
    """User logout endpoint - v1."""
    return jsonify(_add_version_metadata({'message': 'Logged out successfully'})), 200
