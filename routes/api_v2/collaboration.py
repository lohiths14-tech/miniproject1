"""
API v2 Collaboration Blueprint

Enhanced collaboration with video support.
"""

from flask import Blueprint, jsonify, request
from flask import session as flask_session

collaboration_v2_bp = Blueprint('collaboration_v2', __name__, url_prefix='/api/v2/collaboration')


def _add_version_metadata(response_data):
    """Add v2 version metadata to response."""
    response_data['api_version'] = '2.0.0'
    response_data['version'] = 'v2'
    return response_data


@collaboration_v2_bp.route('/create-session', methods=['POST'])
def create_session_v2():
    """Create a new collaboration session - v2 with video support."""
    try:
        from services.collaboration_service import collaboration_service

        data = request.get_json()
        user_id = data.get('user_id') or flask_session.get('user_id', 'demo_user')
        username = data.get('username', 'Anonymous')
        assignment_id = data.get('assignment_id', 'default')
        title = data.get('title')
        is_public = data.get('is_public', False)
        lecturer_assistance = data.get('lecturer_assistance', False)
        enable_video = data.get('enable_video', False)  # V2 feature

        new_session = collaboration_service.create_session(
            host_id=user_id,
            username=username,
            assignment_id=assignment_id,
            title=title,
            is_public=is_public,
            lecturer_assistance=lecturer_assistance,
        )

        session_info = collaboration_service.get_session_info(new_session.session_id)

        # V2: Add video capabilities
        session_info['video_enabled'] = enable_video
        session_info['video_url'] = f'/video/{new_session.session_id}' if enable_video else None

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': session_info,
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v2_bp.route('/join-session', methods=['POST'])
def join_session_v2():
    """Join an existing collaboration session - v2."""
    try:
        from services.collaboration_service import UserRole, collaboration_service

        data = request.get_json()
        session_id = data.get('session_id')
        user_id = data.get('user_id') or flask_session.get('user_id', 'demo_user')
        username = data.get('username', 'Anonymous')
        role = data.get('role', 'participant')
        enable_video = data.get('enable_video', False)

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

        session_info = collaboration_service.get_session_info(session_id)

        # V2: Add video info
        session_info['video_enabled'] = enable_video
        session_info['video_url'] = f'/video/{session_id}' if enable_video else None

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': session_info
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v2_bp.route('/leave-session', methods=['POST'])
def leave_session_v2():
    """Leave current collaboration session - v2."""
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


@collaboration_v2_bp.route('/session/<session_id>', methods=['GET'])
def get_session_info_v2(session_id):
    """Get information about a specific session - v2 with enhanced data."""
    try:
        from services.collaboration_service import collaboration_service

        session_info = collaboration_service.get_session_info(session_id)

        if not session_info:
            return jsonify(_add_version_metadata({
                'status': 'error',
                'message': 'Session not found'
            })), 404

        # V2: Add session analytics
        session_info['analytics'] = {
            'total_edits': 0,
            'active_time_minutes': 0,
            'messages_sent': 0,
        }

        return jsonify(_add_version_metadata({'status': 'success', 'data': session_info}))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v2_bp.route('/public-sessions', methods=['GET'])
def get_public_sessions_v2():
    """Get list of public sessions - v2 with filtering."""
    try:
        from services.collaboration_service import collaboration_service

        public_sessions = collaboration_service.get_public_sessions()

        # V2: Add filtering options
        assignment_filter = request.args.get('assignment_id')
        if assignment_filter:
            public_sessions = [s for s in public_sessions if s.get('assignment_id') == assignment_filter]

        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'sessions': public_sessions,
                'count': len(public_sessions),
                'filters_applied': {'assignment_id': assignment_filter} if assignment_filter else {},
            },
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v2_bp.route('/video/<session_id>/start', methods=['POST'])
def start_video_session_v2(session_id):
    """Start video session - v2 only endpoint."""
    try:
        # V2: Video collaboration feature
        return jsonify(_add_version_metadata({
            'status': 'success',
            'data': {
                'session_id': session_id,
                'video_room_id': f'video_{session_id}',
                'video_url': f'/video/{session_id}',
                'ice_servers': [
                    {'urls': 'stun:stun.l.google.com:19302'},
                ],
            }
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v2_bp.route('/video/<session_id>/stop', methods=['POST'])
def stop_video_session_v2(session_id):
    """Stop video session - v2 only endpoint."""
    try:
        return jsonify(_add_version_metadata({
            'status': 'success',
            'message': 'Video session stopped',
            'session_id': session_id,
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500


@collaboration_v2_bp.route('/request-help', methods=['POST'])
def request_lecturer_help_v2():
    """Request lecturer assistance - v2 with priority."""
    try:
        from services.collaboration_service import collaboration_service

        data = request.get_json()
        session_id = data.get('session_id')
        user_id = data.get('user_id') or flask_session.get('user_id', 'demo_user')
        message = data.get('message', 'Student needs help')
        priority = data.get('priority', 'normal')  # V2 feature

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
            'priority': priority,
        }))

    except Exception as e:
        return jsonify(_add_version_metadata({'status': 'error', 'message': str(e)})), 500
