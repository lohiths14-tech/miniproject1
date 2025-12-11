"""simple_auth module.

This module provides functionality for the AI Grading System.
"""

import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

import simple_auth
from services.otp_service import OTPService

simple_auth_bp = Blueprint("simple_auth", __name__)


def validate_email(email):
    """validate_email function.

    Returns:
        Response data
    """

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_password(password):
    """validate_password function.

    Returns:
        Response data
    """

    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    return True


@simple_auth_bp.route("/login", methods=["POST"])
def simple_login():
    """simple_login function.

    Returns:
        Response data
    """

    try:
        data = request.get_json()

        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password are required"}), 400

        email = data["email"].lower().strip()
        password = data["password"]
        otp_code = data.get("otp")

        # Authenticate user
        user = simple_auth.authenticate_user(email, password)
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        if not user.get("is_active", True):
            return jsonify({"error": "Account is deactivated"}), 401

        # Check 2FA
        if user.get("is_2fa_enabled"):
            if not otp_code:
                return jsonify({"error": "2FA required", "require_2fa": True}), 401

            if not OTPService.verify_otp(user.get("otp_secret"), otp_code):
                return jsonify({"error": "Invalid OTP code"}), 401

        # Create access token
        access_token = create_access_token(identity=email)

        # Remove password hash and secret from response
        user_response = user.copy()
        user_response.pop("password_hash", None)
        user_response.pop("otp_secret", None)

        return (
            jsonify(
                {"message": "Login successful", "access_token": access_token, "user": user_response}
            ),
            200,
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@simple_auth_bp.route("/signup", methods=["POST"])
def simple_signup():
    """simple_signup function.

    Returns:
        Response data
    """

    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["email", "username", "password", "role"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"{field} is required"}), 400

        email = data["email"].lower().strip()
        username = data["username"].strip()
        password = data["password"]
        role = data["role"].lower()

        # Validate email format
        if not validate_email(email):
            return jsonify({"error": "Invalid email format"}), 400

        # Validate password strength
        if not validate_password(password):
            return (
                jsonify(
                    {
                        "error": "Password must be at least 8 characters with uppercase, lowercase, and digit"
                    }
                ),
                400,
            )

        # Validate role
        if role not in ["student", "lecturer"]:
            return jsonify({"error": "Role must be either student or lecturer"}), 400

        # Role-specific validation and registration
        kwargs = {}
        if role == "student":
            if "usn" not in data or not data["usn"]:
                return jsonify({"error": "USN is required for students"}), 400
            kwargs["usn"] = data["usn"]
        else:  # lecturer
            if "lecturer_id" not in data or not data["lecturer_id"]:
                return jsonify({"error": "Lecturer ID is required for lecturers"}), 400
            kwargs["lecturer_id"] = data["lecturer_id"]

        # Register user
        user, error = simple_auth.register_user(email, username, password, role, **kwargs)
        if error:
            return jsonify({"error": error}), 409

        # Create access token
        access_token = create_access_token(identity=email)

        # Remove password hash from response
        user_response = user.copy()
        user_response.pop("password_hash", None)

        return (
            jsonify(
                {
                    "message": "User created successfully",
                    "access_token": access_token,
                    "user": user_response,
                }
            ),
            201,
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"Registration failed: {str(e)}"}), 500


@simple_auth_bp.route("/2fa/setup", methods=["POST"])
def setup_2fa():
    """setup_2fa function.

    Returns:
        Response data
    """

    try:
        data = request.get_json()
        email = data.get("email")  # In real app, get from JWT identity

        if not email:
            return jsonify({"error": "Email required"}), 400

        user = simple_auth.get_user_by_email(email)
        if not user:
            return jsonify({"error": "User not found"}), 404

        # Generate secret
        secret = OTPService.generate_secret()
        uri = OTPService.get_provisioning_uri(secret, email)
        qr_code = OTPService.generate_qr_code(uri)

        # Save secret temporarily (or permanently but disabled)
        user["otp_secret"] = secret
        user["is_2fa_enabled"] = False

        return jsonify({"secret": secret, "qr_code": qr_code}), 200

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"2FA setup failed: {str(e)}"}), 500


@simple_auth_bp.route("/2fa/enable", methods=["POST"])
def enable_2fa():
    """enable_2fa function.

    Returns:
        Response data
    """

    try:
        data = request.get_json()
        email = data.get("email")
        otp_code = data.get("otp")

        if not email or not otp_code:
            return jsonify({"error": "Email and OTP required"}), 400

        user = simple_auth.get_user_by_email(email)
        if not user:
            return jsonify({"error": "User not found"}), 404

        secret = user.get("otp_secret")
        if not secret:
            return jsonify({"error": "2FA not set up"}), 400

        if OTPService.verify_otp(secret, otp_code):
            user["is_2fa_enabled"] = True
            return jsonify({"message": "2FA enabled successfully"}), 200
        else:
            return jsonify({"error": "Invalid OTP"}), 400

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"error": f"2FA enable failed: {str(e)}"}), 500


@simple_auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()

        if not data.get("email"):
            return jsonify({"error": "Email is required"}), 400

        email = data["email"].lower().strip()
        user = simple_auth.get_user_by_email(email)

        if not user:
            # Don't reveal if email exists or not (prevent email enumeration)
            return jsonify({"message": "If the email exists, a reset link has been sent"}), 200

        # Generate reset token
        reset_token = create_access_token(identity=email)

        # Send password reset email
        try:
            from services.email_service import send_password_reset_email
            send_password_reset_email(email, user.get('username', email), reset_token)
            return jsonify({"message": "Password reset email sent successfully"}), 200
        except Exception as e:
            print(f"Failed to send reset email: {str(e)}")
            return jsonify({"error": "Failed to send reset email"}), 500

    except Exception as e:
        return jsonify({"error": f"Password reset failed: {str(e)}"}), 500


@simple_auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    """Reset password with token"""
    from flask_jwt_extended import jwt_required, get_jwt_identity
    from passlib.hash import pbkdf2_sha256

    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Missing or invalid authorization header"}), 401

        # Verify JWT token
        try:
            from flask_jwt_extended import decode_token
            token = auth_header.split(' ')[1]
            decoded = decode_token(token)
            email = decoded.get('sub')
        except Exception as e:
            return jsonify({"msg": "Invalid or expired token"}), 401

        data = request.get_json()

        if not data.get("new_password"):
            return jsonify({"error": "New password is required"}), 400

        new_password = data["new_password"]

        # Validate password strength
        if not validate_password(new_password):
            return jsonify({
                "error": "Password must be at least 8 characters with uppercase, lowercase, and digit"
            }), 400

        user = simple_auth.get_user_by_email(email)

        if not user:
            return jsonify({"error": "User not found"}), 404

        # Update password
        user["password_hash"] = pbkdf2_sha256.hash(new_password)

        return jsonify({"message": "Password reset successfully"}), 200

    except Exception as e:
        return jsonify({"error": f"Password reset failed: {str(e)}"}), 500


@simple_auth_bp.route("/users", methods=["GET"])
def list_users():
    """Debug endpoint to see all users"""
    users = []
    for email, user in simple_auth.USERS_DB.items():
        user_copy = user.copy()
        user_copy.pop("password_hash", None)
        user_copy.pop("otp_secret", None)
        users.append(user_copy)

    return jsonify({"users": users, "count": len(users)})
