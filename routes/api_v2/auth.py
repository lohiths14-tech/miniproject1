"""
API v2 Authentication Blueprint

Enhanced authentication with JWT tokens and improved security features.
"""

import re
from datetime import timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
    get_jwt
)

auth_v2_bp = Blueprint('auth_v2', __name__, url_prefix='/api/v2/auth')


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
    """Add v2 version metadata to response."""
    response_data['api_version'] = '2.0.0'
    response_data['version'] = 'v2'
    return response_data


def _enhanced_user_response(user):
    """Create enhanced user response with additional metadata."""
    user_dict = user.to_dict()
    return {
        **user_dict,
        'permissions': _get_user_permissions(user.role),
        'features': _get_available_features(user.role),
    }


def _get_user_permissions(role):
    """Get permissions based on user role."""
    base_permissions = ['view_assignments', 'submit_code', 'view_grades']
    if role == 'lecturer':
        return base_permissions + ['create_assignments', 'grade_submissions', 'view_analytics', 'manage_students']
    return base_permissions


def _get_available_features(role):
    """Get available features based on user role."""
    base_features = ['gamification', 'collaboration', 'code_review']
    if role == 'lecturer':
        return base_features + ['plagiarism_detection', 'analytics_dashboard', 'assignment_templates']
    return base_features


@auth_v2_bp.route('/signup', methods=['POST'])
def signup_v2():
    """User signup endpoint - v2 with enhanced response."""
    try:
        from models import User
        from services.email_service import send_welcome_email

        data = request.get_json()

        required_fields = ['email', 'username', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify(_add_version_metadata({'error': f'{field} is required'})), 400

        email = data['email'].lower().strip()
        username = data['username'].strip()
        password = data['password']
        role = data['role'].lower()

        if not validate_email(email):
            return jsonify(_add_version_metadata({'error': 'Invalid email format'})), 400

        if not validate_password(password):
            return jsonify(_add_version_metadata({
                'error': 'Password must be at least 8 characters with uppercase, lowercase, and digit'
            })), 400

        if role not in ['student', 'lecturer']:
            return jsonify(_add_version_metadata({'error': 'Role must be either student or lecturer'})), 400

        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify(_add_version_metadata({'error': 'User with this email already exists'})), 409

        if role == 'student':
            if 'usn' not in data or not data['usn']:
                return jsonify(_add_version_metadata({'error': 'USN is required for students'})), 400
            user = User(email, username, password, role, usn=data['usn'])
        else:
            if 'lecturer_id' not in data or not data['lecturer_id']:
                return jsonify(_add_version_metadata({'error': 'Lecturer ID is required for lecturers'})), 400
            user = User(email, username, password, role, lecturer_id=data['lecturer_id'])

        user.save()

        try:
            send_welcome_email(email, username, role)
        except Exception as e:
            print(f'Failed to send welcome email: {str(e)}')

        # V2: Include both access and refresh tokens
        access_token = create_access_token(identity=str(user._id), expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity=str(user._id))

        return jsonify(_add_version_metadata({
            'message': 'User created successfully',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user': _enhanced_user_response(user),
        })), 201

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Registration failed: {str(e)}'})), 500


@auth_v2_bp.route('/login', methods=['POST'])
def login_v2():
    """User login endpoint - v2 with JWT tokens."""
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

        # V2: Include both access and refresh tokens
        access_token = create_access_token(identity=str(user._id), expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity=str(user._id))

        return jsonify(_add_version_metadata({
            'message': 'Login successful',
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
            'user': _enhanced_user_response(user),
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Login failed: {str(e)}'})), 500


@auth_v2_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token_v2():
    """Refresh access token - v2 only."""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id, expires_delta=timedelta(hours=1))

        return jsonify(_add_version_metadata({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': 3600,
        })), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Token refresh failed: {str(e)}'})), 500


@auth_v2_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile_v2():
    """Get user profile endpoint - v2 with enhanced data."""
    try:
        from models import User

        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)

        if not user:
            return jsonify(_add_version_metadata({'error': 'User not found'})), 404

        return jsonify(_add_version_metadata({'user': _enhanced_user_response(user)})), 200

    except Exception as e:
        return jsonify(_add_version_metadata({'error': f'Failed to get profile: {str(e)}'})), 500


@auth_v2_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout_v2():
    """User logout endpoint - v2."""
    # In production, you would blacklist the token here
    return jsonify(_add_version_metadata({'message': 'Logged out successfully'})), 200
