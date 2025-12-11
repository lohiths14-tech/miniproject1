"""
Security Dashboard API Routes
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.security_audit_service import SecurityAuditService, SecurityEventType
from pymongo import MongoClient
from datetime import datetime, timedelta
import os

security_bp = Blueprint('security', __name__, url_prefix='/api/security')

# Initialize service
client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
db = client[os.getenv('DB_NAME', 'ai_grading')]
audit_service = SecurityAuditService(db)


@security_bp.route('/metrics', methods=['GET'])
@jwt_required()
def get_security_metrics():
    """
    Get security metrics for dashboard

    Query params:
        hours: Time window in hours (default: 24)
    """
    try:
        # Check if user is admin/lecturer
        user_id = get_jwt_identity()
        # TODO: Add role check

        hours = request.args.get('hours', 24, type=int)

        metrics = audit_service.get_security_metrics(hours)

        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/activity', methods=['GET'])
@jwt_required()
def get_user_activity():
    """
    Get security activity for current user

    Query params:
        limit: Maximum number of events (default: 100)
    """
    try:
        user_id = get_jwt_identity()
        limit = request.args.get('limit', 100, type=int)

        activity = audit_service.get_user_activity(user_id, limit)

        # Convert ObjectId to string for JSON serialization
        for event in activity:
            event['_id'] = str(event['_id'])
            event['timestamp'] = event['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'activity': activity
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/suspicious', methods=['GET'])
@jwt_required()
def get_suspicious_activity():
    """
    Get suspicious security events (admin only)

    Query params:
        hours: Time window in hours (default: 24)
        limit: Maximum number of events (default: 100)
    """
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        # TODO: Add admin role check

        hours = request.args.get('hours', 24, type=int)
        limit = request.args.get('limit', 100, type=int)

        suspicious = audit_service.get_suspicious_activity(hours, limit)

        # Convert for JSON
        for event in suspicious:
            event['_id'] = str(event['_id'])
            event['timestamp'] = event['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'suspicious_events': suspicious
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/failed-logins', methods=['GET'])
@jwt_required()
def get_failed_logins():
    """
    Get failed login attempts (admin only)

    Query params:
        email: Filter by email
        minutes: Time window in minutes (default: 30)
    """
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        # TODO: Add admin role check

        email = request.args.get('email')
        minutes = request.args.get('minutes', 30, type=int)

        if not email:
            return jsonify({'error': 'Email parameter required'}), 400

        failed_attempts = audit_service.get_failed_attempts(email, minutes)

        # Convert for JSON
        for attempt in failed_attempts:
            attempt['_id'] = str(attempt['_id'])
            attempt['timestamp'] = attempt['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'failed_attempts': failed_attempts,
            'count': len(failed_attempts)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/export', methods=['POST'])
@jwt_required()
def export_audit_log():
    """
    Export audit log for compliance (admin only)

    Body:
        start_date: Start date (ISO format)
        end_date: End date (ISO format)
        format: Export format (json, csv)
    """
    try:
        # Check if user is admin
        user_id = get_jwt_identity()
        # TODO: Add admin role check

        data = request.json
        start_date = datetime.fromisoformat(data.get('start_date'))
        end_date = datetime.fromisoformat(data.get('end_date'))
        format = data.get('format', 'json')

        events = audit_service.export_audit_log(start_date, end_date, format)

        # Convert for JSON
        for event in events:
            event['_id'] = str(event['_id'])
            event['timestamp'] = event['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'events': events,
            'count': len(events),
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@security_bp.route('/dashboard-data', methods=['GET'])
@jwt_required()
def get_dashboard_data():
    """
    Get comprehensive security dashboard data
    """
    try:
        user_id = get_jwt_identity()

        # Get metrics for different time windows
        metrics_24h = audit_service.get_security_metrics(24)
        metrics_7d = audit_service.get_security_metrics(24 * 7)

        # Get recent suspicious activity
        suspicious = audit_service.get_suspicious_activity(24, 10)
        for event in suspicious:
            event['_id'] = str(event['_id'])
            event['timestamp'] = event['timestamp'].isoformat()

        # Get user's recent activity
        user_activity = audit_service.get_user_activity(user_id, 10)
        for event in user_activity:
            event['_id'] = str(event['_id'])
            event['timestamp'] = event['timestamp'].isoformat()

        return jsonify({
            'success': True,
            'dashboard': {
                'metrics_24h': metrics_24h,
                'metrics_7d': metrics_7d,
                'recent_suspicious': suspicious,
                'user_activity': user_activity
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
