"""
API v1 Collaboration Blueprint

Wraps existing collaboration functionality with v1 versioned endpoints.
"""

from flask import Blueprint, jsonify, request
from flask import session as flask_session

collaboration_v1_bp = Blueprint('collaboration_v1', __name__, url_prefix='/api/v1/collaboration')


def _add_version_metadata(response_data):
    """Add v1 version metadata to response."""
    response_data['api_version'] = '1.0.0'
    response_data['version'] = 'v1'
    return response_data


@collaboration_v1_bp.route('/create-session', methods=['POST'])
def create_session_v1():
    """Create a new collaboration session - v1."""
    try:
        from services.collaboration_service import collaboration_service

        data = request.get_json()
        user_id = data.get('user_id') or flask_session.get('user_id', 'demo_user')
        username = data.get('username', 'Anonymous')
        assignment_id = data.get('assignment_id', 'default')
        title = data.get('title')
        is_public = data.get('is_public', False)
        lecturer_assistance = data.get('lecturer_assistance', False)

        new_session = collaboration_service.create_session(
            host_id=user_id,
            username=username,
            assignment_id=assignment_id,
            title=title,
            is_public=is_public,
            lecturer_assistance=lecturer_assistance,
        )

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': collaboration_service.get_session_info(new_session.session_id),
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v1_bp.route('/join-session', methods=['POST'])
def join_session_v1():
    """Join an existing collaboration session - v1."""
    try:
        from services.collaboration_service import UserRole, collaboration_service

        data = request.get_json()
        session_id = data.get('session_id')
        user_id = data.get('user_id') or flask_session.get('user_id', 'demo_user')
        username = data.get('username', 'Anonymous')
        role = data.get('role', 'participant')

        if not session_id:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Session ID is required'
            })), 400

        user_role = UserRole.LECTURER if role == 'lecturer' else UserRole.PARTICIPANT
        joined_session = collaboration_service.join_session(
            session_id=session_id, user_id=user_id, username=username, role=user_role
        )

        if not joined_session:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Unable to join session (not found or full)'
            })), 404

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': collaboration_service.get_session_info(session_id)
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v1_bp.route('/leave-session', methods=['POST'])
def leave_session_v1():
    """Leave current collaboration session - v1."""
    try:
        from services.collaboration_service import collaboration_service

        data = request.get_json()
        user_id = data.get('user_id') or flask_session.get('user_id', 'demo_user')

        success = collaboration_service.leave_session(user_id)

        return jsonify(_add_version_metadata({
            'status': 'success' if success else 'error',
            'message': 'Left session successfully' if success else 'No active session found',
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v1_bp.route('/session/<session_id>', methods=['GET'])
def get_session_info_v1(session_id):
    """Get information about a specific session - v1."""
    try:
        from services.collaboration_service import collaboration_service

        session_info = collaboration_service.get_session_info(session_id)

        if not session_info:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Session not found'
            })), 404

        return jsonify(_add_version_metadata({'status': 'success', 'data': session_info}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v1_bp.route('/public-sessions', methods=['GET'])
def get_public_sessions_v1():
    """Get list of public sessions available to join - v1."""
    try:
        from services.collaboration_service import collaboration_service

        public_sessions = collaboration_service.get_public_sessions()

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {'sessions': public_sessions, 'count': len(public_sessions)},
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v1_bp.route('/request-help', methods=['POST'])
def request_lecturer_help_v1():
    """Request lecturer assistance for a session - v1."""
    try:
        from services.collaboration_service import collaboration_service

        data = request.get_json()
        session_id = data.get('session_id')
        user_id = data.get('user_id') or flask_session.get('user_id', 'demo_user')
        message = data.get('message', 'Student needs help')

        if not session_id:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Session ID is required'
            })), 400

        success = collaboration_service.request_lecturer_assistance(
            session_id=session_id, user_id=user_id, message=message
        )

        return jsonify(_add_version_metadata({
            'status': 'success' if success else 'error',
            'message': 'Help request sent' if success else 'Failed to send help request',
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v1_bp.route('/session/<session_id>/recording', methods=['GET'])
def get_session_recording_v1(session_id):
    """Get session recording for playback - v1."""
    try:
        from services.collaboration_service import collaboration_service

        recording = collaboration_service.get_session_recording(session_id)

        if not recording:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Recording not found'
            })), 404

        return jsonify(_add_version_metadata({'status': 'success', 'data': recording}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500

