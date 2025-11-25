from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
import simple_auth
import re

simple_auth_bp = Blueprint('simple_auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

@simple_auth_bp.route('/login', methods=['POST'])
def simple_login():
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Authenticate user
        user = simple_auth.authenticate_user(email, password)
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.get('is_active', True):
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create access token
        access_token = create_access_token(identity=email)
        
        # Remove password hash from response
        user_response = user.copy()
        user_response.pop('password_hash', None)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user_response
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@simple_auth_bp.route('/signup', methods=['POST'])
def simple_signup():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['email', 'username', 'password', 'role']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'{field} is required'}), 400
        
        email = data['email'].lower().strip()
        username = data['username'].strip()
        password = data['password']
        role = data['role'].lower()
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if not validate_password(password):
            return jsonify({
                'error': 'Password must be at least 8 characters with uppercase, lowercase, and digit'
            }), 400
        
        # Validate role
        if role not in ['student', 'lecturer']:
            return jsonify({'error': 'Role must be either student or lecturer'}), 400
        
        # Role-specific validation and registration
        kwargs = {}
        if role == 'student':
            if 'usn' not in data or not data['usn']:
                return jsonify({'error': 'USN is required for students'}), 400
            kwargs['usn'] = data['usn']
        else:  # lecturer
            if 'lecturer_id' not in data or not data['lecturer_id']:
                return jsonify({'error': 'Lecturer ID is required for lecturers'}), 400
            kwargs['lecturer_id'] = data['lecturer_id']
        
        # Register user
        user, error = simple_auth.register_user(email, username, password, role, **kwargs)
        if error:
            return jsonify({'error': error}), 409
        
        # Create access token
        access_token = create_access_token(identity=email)
        
        # Remove password hash from response
        user_response = user.copy()
        user_response.pop('password_hash', None)
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user_response
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@simple_auth_bp.route('/users', methods=['GET'])
def list_users():
    """Debug endpoint to see all users"""
    users = []
    for email, user in simple_auth.USERS_DB.items():
        user_copy = user.copy()
        user_copy.pop('password_hash', None)
        users.append(user_copy)
    
    return jsonify({'users': users, 'count': len(users)})