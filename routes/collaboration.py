"""Collaboration API Routes.

This module handles real-time collaboration endpoints for WebSocket-based
pair programming and code sharing sessions.
"""

from datetime import datetime

from flask import Blueprint, jsonify, request
from flask import session as flask_session

try:
    from flask_socketio import emit, join_room, leave_room
except ImportError:
    # Graceful fallback if flask-socketio not installed
    emit = lambda *args, **kwargs: None
    join_room = lambda *args, **kwargs: None
    leave_room = lambda *args, **kwargs: None

try:
    from services.collaboration_service import UserRole, collaboration_service
except ImportError:
    # Graceful fallback
    collaboration_service = None
    UserRole = None

# Create blueprint
collaboration_bp = Blueprint("collaboration", __name__)

# WebSocket events will be handled by SocketIO
# This blueprint handles REST API endpoints


@collaboration_bp.route("/create-session", methods=["POST"])
def create_session():
    """Create a new collaboration session.

    Returns:
        JSON response with session information or error message
    """
    try:
        data = request.get_json()
        user_id = data.get("user_id") or flask_session.get("user_id", "demo_user")
        username = data.get("username", "Anonymous")
        assignment_id = data.get("assignment_id", "default")
        title = data.get("title")
        is_public = data.get("is_public", False)
        lecturer_assistance = data.get("lecturer_assistance", False)

        # Create new session
        new_session = collaboration_service.create_session(
            host_id=user_id,
            username=username,
            assignment_id=assignment_id,
            title=title,
            is_public=is_public,
            lecturer_assistance=lecturer_assistance,
        )

        return jsonify(
            {
                "status": "success",
                "data": collaboration_service.get_session_info(new_session.session_id),
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@collaboration_bp.route("/join-session", methods=["POST"])
def join_session():
    """Join an existing collaboration session"""
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        user_id = data.get("user_id") or flask_session.get("user_id", "demo_user")
        username = data.get("username", "Anonymous")
        role = data.get("role", "participant")

        if not session_id:
            return jsonify({"status": "error", "message": "Session ID is required"}), 400

        # Join session
        user_role = UserRole.LECTURER if role == "lecturer" else UserRole.PARTICIPANT
        joined_session = collaboration_service.join_session(
            session_id=session_id, user_id=user_id, username=username, role=user_role
        )

        if not joined_session:
            return (
                jsonify(
                    {"status": "error", "message": "Unable to join session (not found or full)"}
                ),
                404,
            )

        return jsonify(
            {"status": "success", "data": collaboration_service.get_session_info(session_id)}
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@collaboration_bp.route("/leave-session", methods=["POST"])
def leave_session():
    """Leave current collaboration session"""
    try:
        data = request.get_json()
        user_id = data.get("user_id") or flask_session.get("user_id", "demo_user")

        success = collaboration_service.leave_session(user_id)

        return jsonify(
            {
                "status": "success" if success else "error",
                "message": "Left session successfully" if success else "No active session found",
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@collaboration_bp.route("/session/<session_id>", methods=["GET"])
def get_session_info(session_id):
    """Get information about a specific session"""
    try:
        session_info = collaboration_service.get_session_info(session_id)

        if not session_info:
            return jsonify({"status": "error", "message": "Session not found"}), 404

        return jsonify({"status": "success", "data": session_info})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@collaboration_bp.route("/public-sessions", methods=["GET"])
def get_public_sessions():
    """Get list of public sessions available to join"""
    try:
        public_sessions = collaboration_service.get_public_sessions()

        return jsonify(
            {
                "status": "success",
                "data": {"sessions": public_sessions, "count": len(public_sessions)},
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@collaboration_bp.route("/request-help", methods=["POST"])
def request_lecturer_help():
    """Request lecturer assistance for a session"""
    try:
        data = request.get_json()
        session_id = data.get("session_id")
        user_id = data.get("user_id") or flask_session.get("user_id", "demo_user")
        message = data.get("message", "Student needs help")

        if not session_id:
            return jsonify({"status": "error", "message": "Session ID is required"}), 400

        success = collaboration_service.request_lecturer_assistance(
            session_id=session_id, user_id=user_id, message=message
        )

        return jsonify(
            {
                "status": "success" if success else "error",
                "message": "Help request sent" if success else "Failed to send help request",
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@collaboration_bp.route("/session/<session_id>/recording", methods=["GET"])
def get_session_recording(session_id):
    """Get session recording for playback"""
    try:
        recording = collaboration_service.get_session_recording(session_id)

        if not recording:
            return jsonify({"status": "error", "message": "Recording not found"}), 404

        return jsonify({"status": "success", "data": recording})

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@collaboration_bp.route("/demo/create-sample-session", methods=["POST"])
def create_sample_session():
    """Create a sample collaboration session for demo purposes"""
    try:
        # Create a sample session
        session = collaboration_service.create_session(
            host_id="demo_host",
            username="Alice Coder",
            assignment_id="fibonacci_assignment",
            title="Fibonacci Algorithm Collaboration",
            is_public=True,
            lecturer_assistance=True,
        )

        # Add sample participants
        collaboration_service.join_session(
            session_id=session.session_id,
            user_id="demo_participant1",
            username="Bob Developer",
            role=UserRole.PARTICIPANT,
        )

        # Add some sample code changes
        collaboration_service.apply_code_change(
            "demo_host",
            {
                "operation": "insert",
                "position": 0,
                "content": "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            },
        )

        return jsonify(
            {
                "status": "success",
                "data": {
                    "session_id": session.session_id,
                    "session_info": collaboration_service.get_session_info(session.session_id),
                    "message": "Sample session created successfully",
                },
            }
        )

    except (ValueError, KeyError, AttributeError) as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# WebSocket Event Handlers (to be used with Flask-SocketIO)
def setup_websocket_events(socketio):
    """Setup WebSocket event handlers for real-time collaboration"""

    @socketio.on("join_collaboration")
    def handle_join_collaboration(data):
        """Handle user joining a collaboration session"""
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        username = data.get("username", "Anonymous")

        if session_id and user_id:
            # Join the room for this session
            join_room(session_id)

            # Register WebSocket connection
            collaboration_service.register_websocket(user_id, request.sid)

            # Get current session state
            session_info = collaboration_service.get_session_info(session_id)

            if session_info:
                # Send current state to joining user
                emit("session_state", {"type": "session_joined", "session": session_info})

                # Notify other participants
                emit(
                    "user_activity",
                    {
                        "type": "user_joined",
                        "user_id": user_id,
                        "username": username,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    room=session_id,
                    include_self=False,
                )

    @socketio.on("leave_collaboration")
    def handle_leave_collaboration(data):
        """Handle user leaving a collaboration session"""
        session_id = data.get("session_id")
        user_id = data.get("user_id")

        if session_id and user_id:
            # Leave the room
            leave_room(session_id)

            # Unregister WebSocket connection
            collaboration_service.unregister_websocket(user_id)

            # Leave the session
            collaboration_service.leave_session(user_id)

            # Notify other participants
            emit(
                "user_activity",
                {
                    "type": "user_left",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                room=session_id,
            )

    @socketio.on("code_change")
    def handle_code_change(data):
        """Handle real-time code changes"""
        user_id = data.get("user_id")
        change_data = data.get("change", {})

        if user_id and collaboration_service.apply_code_change(user_id, change_data):
            # Get session ID for this user
            session_id = collaboration_service.user_sessions.get(user_id)

            if session_id:
                # Broadcast change to all participants in the session
                emit(
                    "code_update",
                    {
                        "type": "code_changed",
                        "change": change_data,
                        "user_id": user_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    room=session_id,
                    include_self=False,
                )

    @socketio.on("cursor_move")
    def handle_cursor_move(data):
        """Handle cursor position updates"""
        user_id = data.get("user_id")
        position = data.get("position", 0)

        if user_id and collaboration_service.update_cursor_position(user_id, position):
            # Get session ID for this user
            session_id = collaboration_service.user_sessions.get(user_id)

            if session_id:
                # Broadcast cursor position to other participants
                emit(
                    "cursor_update",
                    {
                        "type": "cursor_moved",
                        "user_id": user_id,
                        "position": position,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    room=session_id,
                    include_self=False,
                )

    @socketio.on("chat_message")
    def handle_chat_message(data):
        """Handle chat messages in collaboration session"""
        user_id = data.get("user_id")
        message = data.get("message", "")
        username = data.get("username", "Anonymous")

        # Get session ID for this user
        session_id = collaboration_service.user_sessions.get(user_id)

        if session_id and message.strip():
            # Broadcast chat message to all participants
            emit(
                "chat_update",
                {
                    "type": "chat_message",
                    "user_id": user_id,
                    "username": username,
                    "message": message,
                    "timestamp": datetime.utcnow().isoformat(),
                },
                room=session_id,
            )

    @socketio.on("request_help")
    def handle_help_request(data):
        """Handle lecturer help requests"""
        session_id = data.get("session_id")
        user_id = data.get("user_id")
        message = data.get("message", "Student needs assistance")

        if session_id and user_id:
            success = collaboration_service.request_lecturer_assistance(
                session_id=session_id, user_id=user_id, message=message
            )

            if success:
                # Notify all participants that help was requested
                emit(
                    "help_requested",
                    {
                        "type": "help_requested",
                        "user_id": user_id,
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    room=session_id,
                )

                # Send confirmation to requester
                emit(
                    "help_request_sent",
                    {"status": "success", "message": "Help request sent to available lecturers"},
                )
            else:
                emit(
                    "help_request_sent",
                    {"status": "error", "message": "Failed to send help request"},
                )

    @socketio.on("disconnect")
    def handle_disconnect():
        """Handle WebSocket disconnection"""
        # Find user by socket ID and remove from sessions
        for user_id, ws in list(collaboration_service.websocket_connections.items()):
            if ws == request.sid:
                collaboration_service.leave_session(user_id)
                collaboration_service.unregister_websocket(user_id)
                break

    return socketio
