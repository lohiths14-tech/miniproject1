from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import User
from services.email_service import send_welcome_email, send_password_reset_email
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    # At least 8 characters, one uppercase, one lowercase, one digit
    if len(password) < 8:
        return False
    if not re.search(r'[A-Z]', password):
        return False
    if not re.search(r'[a-z]', password):
        return False
    if not re.search(r'\d', password):
        return False
    return True

@auth_bp.route('/signup', methods=['POST'])
def signup():
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
        
        # Check if user already exists
        existing_user = User.find_by_email(email)
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Role-specific validation
        if role == 'student':
            if 'usn' not in data or not data['usn']:
                return jsonify({'error': 'USN is required for students'}), 400
            user = User(email, username, password, role, usn=data['usn'])
        else:  # lecturer
            if 'lecturer_id' not in data or not data['lecturer_id']:
                return jsonify({'error': 'Lecturer ID is required for lecturers'}), 400
            user = User(email, username, password, role, lecturer_id=data['lecturer_id'])
        
        # Save user to database
        user.save()
        
        # Send welcome email
        try:
            send_welcome_email(email, username, role)
        except Exception as e:
            print(f"Failed to send welcome email: {str(e)}")
        
        # Create access token
        access_token = create_access_token(identity=str(user._id))
        
        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Find user by email
        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user._id))
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': f'Failed to get profile: {str(e)}'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()
        
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        user = User.find_by_email(email)
        
        if not user:
            # Don't reveal if email exists or not
            return jsonify({'message': 'If the email exists, a reset link has been sent'}), 200
        
        # Generate reset token
        reset_token = create_access_token(identity=str(user._id), expires_delta=False)
        
        # Send password reset email
        try:
            send_password_reset_email(email, user.username, reset_token)
            return jsonify({'message': 'Password reset email sent successfully'}), 200
        except Exception as e:
            print(f"Failed to send reset email: {str(e)}")
            return jsonify({'error': 'Failed to send reset email'}), 500
        
    except Exception as e:
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
@jwt_required()
def reset_password():
    try:
        data = request.get_json()
        
        if not data.get('new_password'):
            return jsonify({'error': 'New password is required'}), 400
        
        new_password = data['new_password']
        
        # Validate password strength
        if not validate_password(new_password):
            return jsonify({
                'error': 'Password must be at least 8 characters with uppercase, lowercase, and digit'
            }), 400
        
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Update password
        from passlib.hash import pbkdf2_sha256
        user.password_hash = pbkdf2_sha256.hash(new_password)
        user.save()
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': f'Password reset failed: {str(e)}'}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    # In a more sophisticated implementation, you would blacklist the token
    return jsonify({'message': 'Logged out successfully'}), 200