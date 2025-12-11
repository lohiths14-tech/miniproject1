"""
Multi-Factor Authentication API Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.mfa_service import MFAService
from services.security_audit_service import SecurityAuditService, SecurityEventType
from pymongo import MongoClient
import os

mfa_bp = Blueprint('mfa', __name__, url_prefix='/api/mfa')

# Initialize services
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client[os.getenv('DB_NAME', 'ai_grading')]
mfa_service = MFAService(db)
audit_service = SecurityAuditService(db)


@mfa_bp.route('/setup', methods=['POST'])
@jwt_required()
def setup_mfa():
    """
    Initialize MFA setup for a user

    Returns QR code and secret for TOTP app setup
    """
    try:
        user_id = get_jwt_identity()
        user_email = request.json.get('email')

        if not user_email:
            return jsonify({'error': 'Email required'}), 400

        # Generate secret
        secret = mfa_service.generate_secret(user_id)

        # Generate QR code
        qr_code = mfa_service.generate_qr_code(user_email, secret)

        # Log event
        audit_service.log_event(
            SecurityEventType.MFA_ENABLED,
            user_id=user_id,
            ip_address=request.remote_addr,
            details={'step': 'setup_initiated'}
        )

        return jsonify({
            'success': True,
            'secret': secret,
            'qr_code': qr_code,
            'message': 'Scan QR code with your authenticator app'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mfa_bp.route('/verify-setup', methods=['POST'])
@jwt_required()
def verify_mfa_setup():
    """
    Verify MFA setup with a test token

    Enables MFA if token is valid
    """
    try:
        user_id = get_jwt_identity()
        token = request.json.get('token')

        if not token:
            return jsonify({'error': 'Token required'}), 400

        # Enable MFA
        success, message = mfa_service.enable_mfa(user_id, token)

        if success:
            # Log success
            audit_service.log_event(
                SecurityEventType.MFA_ENABLED,
                user_id=user_id,
                ip_address=request.remote_addr,
                details={'step': 'enabled'},
                severity='info'
            )

            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            # Log failure
            audit_service.log_event(
                SecurityEventType.MFA_VERIFICATION_FAILURE,
                user_id=user_id,
                ip_address=request.remote_addr,
                severity='warning'
            )

            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mfa_bp.route('/verify', methods=['POST'])
@jwt_required()
def verify_mfa_token():
    """
    Verify MFA token during login
    """
    try:
        user_id = get_jwt_identity()
        token = request.json.get('token')

        if not token:
            return jsonify({'error': 'Token required'}), 400

        # Verify token
        is_valid = mfa_service.verify_token(user_id, token)

        if is_valid:
            audit_service.log_event(
                SecurityEventType.MFA_VERIFICATION_SUCCESS,
                user_id=user_id,
                ip_address=request.remote_addr
            )

            return jsonify({
                'success': True,
                'message': 'Token verified'
            }), 200
        else:
            audit_service.log_event(
                SecurityEventType.MFA_VERIFICATION_FAILURE,
                user_id=user_id,
                ip_address=request.remote_addr,
                severity='warning'
            )

            return jsonify({
                'success': False,
                'error': 'Invalid token'
            }), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mfa_bp.route('/backup-codes', methods=['POST'])
@jwt_required()
def generate_backup_codes():
    """
    Generate new backup codes
    """
    try:
        user_id = get_jwt_identity()

        # Generate backup codes
        codes = mfa_service.generate_backup_codes(user_id)

        audit_service.log_event(
            SecurityEventType.MFA_ENABLED,
            user_id=user_id,
            ip_address=request.remote_addr,
            details={'action': 'backup_codes_generated'}
        )

        return jsonify({
            'success': True,
            'backup_codes': codes,
            'message': 'Save these codes in a secure location'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mfa_bp.route('/verify-backup', methods=['POST'])
@jwt_required()
def verify_backup_code():
    """
    Verify backup code for MFA recovery
    """
    try:
        user_id = get_jwt_identity()
        code = request.json.get('code')

        if not code:
            return jsonify({'error': 'Backup code required'}), 400

        # Verify backup code
        is_valid = mfa_service.verify_backup_code(user_id, code)

        if is_valid:
            audit_service.log_event(
                SecurityEventType.MFA_VERIFICATION_SUCCESS,
                user_id=user_id,
                ip_address=request.remote_addr,
                details={'method': 'backup_code'}
            )

            return jsonify({
                'success': True,
                'message': 'Backup code verified'
            }), 200
        else:
            audit_service.log_event(
                SecurityEventType.MFA_VERIFICATION_FAILURE,
                user_id=user_id,
                ip_address=request.remote_addr,
                details={'method': 'backup_code'},
                severity='warning'
            )

            return jsonify({
                'success': False,
                'error': 'Invalid backup code'
            }), 401

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mfa_bp.route('/disable', methods=['POST'])
@jwt_required()
def disable_mfa():
    """
    Disable MFA for a user
    """
    try:
        user_id = get_jwt_identity()
        password = request.json.get('password')

        if not password:
            return jsonify({'error': 'Password required'}), 400

        # Disable MFA
        success, message = mfa_service.disable_mfa(user_id, password)

        if success:
            audit_service.log_event(
                SecurityEventType.MFA_DISABLED,
                user_id=user_id,
                ip_address=request.remote_addr,
                severity='warning'
            )

            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mfa_bp.route('/status', methods=['GET'])
@jwt_required()
def get_mfa_status():
    """
    Get MFA status for current user
    """
    try:
        user_id = get_jwt_identity()

        status = mfa_service.get_mfa_status(user_id)

        return jsonify({
            'success': True,
            'status': status
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
