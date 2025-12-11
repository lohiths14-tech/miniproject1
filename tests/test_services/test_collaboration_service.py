"""Tests for Collaboration Service.

Tests session management, real-time sync, and participant handling.
Requirements: 2.1, 2.2
"""
import pytest
from services.collaboration_service import (
    CollaborationService,
    SessionStatus,
    UserRole,
)


class TestCollaborationServiceInit:
    """Test suite for CollaborationService initialization."""

    def test_service_initialization(self):
        """Test that service initializes correctly."""
        service = CollaborationService()

        assert service is not None
        assert isinstance(service.active_sessions, dict)
        assert isinstance(service.user_sessions, dict)
        assert isinstance(service.websocket_connections, dict)
        assert isinstance(service.session_recordings, dict)


class TestSessionCreation:
    """Test suite for session creation."""

    def test_create_session_basic(self):
        """Test basic session creation."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assign_001",
        )

        assert session is not None
        assert session.host_id == "host_123"
        assert session.assignment_id == "assign_001"
        assert session.status == SessionStatus.WAITING
        assert "host_123" in session.participants

    def test_create_session_with_title(self):
        """Test session creation with custom title."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assign_001",
            title="My Coding Session",
        )

        assert session.title == "My Coding Session"

    def test_create_session_default_title(self):
        """Test session creation generates default title."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assign_001",
        )

        assert "TestHost" in session.title
        assert "Coding Session" in session.title

    def test_create_public_session(self):
        """Test creating a public session."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assign_001",
            is_public=True,
        )

        assert session.is_public is True

    def test_create_session_with_lecturer_assistance(self):
        """Test creating session with lecturer assistance enabled."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assign_001",
            lecturer_assistance=True,
        )

        assert session.lecturer_assistance is True

    def test_host_is_participant(self):
        """Test that host is added as participant."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assign_001",
        )

        assert "host_123" in session.participants
        participant = session.participants["host_123"]
        assert participant.role == UserRole.HOST
        assert participant.username == "TestHost"
        assert participant.is_online is True


class TestJoinSession:
    """Test suite for joining sessions."""

    def test_join_session_success(self):
        """Test successfully joining a session."""
        service = CollaborationService()

        # Create session
        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        # Join session
        result = service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        assert result is not None
        assert "user_456" in result.participants
        assert result.participants["user_456"].role == UserRole.PARTICIPANT

    def test_join_nonexistent_session(self):
        """Test joining a non-existent session."""
        service = CollaborationService()

        result = service.join_session(
            session_id="nonexistent",
            user_id="user_123",
            username="User",
        )

        assert result is None

    def test_join_session_activates_waiting_session(self):
        """Test that joining activates a waiting session."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        assert session.status == SessionStatus.WAITING

        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        assert session.status == SessionStatus.ACTIVE

    def test_join_session_as_lecturer(self):
        """Test joining session as lecturer."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        result = service.join_session(
            session_id=session.session_id,
            user_id="lecturer_001",
            username="Lecturer",
            role=UserRole.LECTURER,
        )

        assert result is not None
        assert result.participants["lecturer_001"].role == UserRole.LECTURER

    def test_rejoin_session_updates_status(self):
        """Test that rejoining updates user status."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        # Join first time
        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        # Leave
        service.leave_session("user_456")

        # Rejoin
        result = service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        assert result is not None
        assert result.participants["user_456"].is_online is True


class TestLeaveSession:
    """Test suite for leaving sessions."""

    def test_leave_session_success(self):
        """Test successfully leaving a session."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        result = service.leave_session("user_456")

        assert result is True
        assert session.participants["user_456"].is_online is False

    def test_leave_session_not_in_session(self):
        """Test leaving when not in any session."""
        service = CollaborationService()

        result = service.leave_session("nonexistent_user")

        assert result is False

    def test_host_leaving_ends_session(self):
        """Test that host leaving ends the session."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        service.leave_session("host_123")

        assert session.status == SessionStatus.ENDED


class TestCodeChanges:
    """Test suite for code change operations."""

    def test_apply_code_change_insert(self):
        """Test applying an insert code change."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        # Activate session
        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        original_content = session.code_content

        result = service.apply_code_change(
            user_id="host_123",
            change_data={
                "operation": "insert",
                "position": 0,
                "content": "# New comment\n",
            },
        )

        assert result is True
        assert session.code_content.startswith("# New comment\n")
        assert len(session.change_history) == 1

    def test_apply_code_change_delete(self):
        """Test applying a delete code change."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        # Set known content
        session.code_content = "Hello World"

        result = service.apply_code_change(
            user_id="host_123",
            change_data={
                "operation": "delete",
                "position": 0,
                "length": 6,
            },
        )

        assert result is True
        assert session.code_content == "World"

    def test_apply_code_change_replace(self):
        """Test applying a replace code change."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        session.code_content = "Hello World"

        result = service.apply_code_change(
            user_id="host_123",
            change_data={
                "operation": "replace",
                "position": 0,
                "content": "Hi",
                "length": 5,
            },
        )

        assert result is True
        assert session.code_content == "Hi World"

    def test_apply_code_change_not_in_session(self):
        """Test applying change when not in session."""
        service = CollaborationService()

        result = service.apply_code_change(
            user_id="nonexistent",
            change_data={"operation": "insert", "position": 0, "content": "test"},
        )

        assert result is False

    def test_apply_code_change_inactive_session(self):
        """Test applying change to inactive session."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        # Session is WAITING, not ACTIVE
        result = service.apply_code_change(
            user_id="host_123",
            change_data={"operation": "insert", "position": 0, "content": "test"},
        )

        assert result is False


class TestCursorPosition:
    """Test suite for cursor position updates."""

    def test_update_cursor_position(self):
        """Test updating cursor position."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        result = service.update_cursor_position("host_123", 42)

        assert result is True
        assert session.participants["host_123"].cursor_position == 42

    def test_update_cursor_not_in_session(self):
        """Test updating cursor when not in session."""
        service = CollaborationService()

        result = service.update_cursor_position("nonexistent", 10)

        assert result is False


class TestLecturerAssistance:
    """Test suite for lecturer assistance requests."""

    def test_request_lecturer_assistance(self):
        """Test requesting lecturer assistance."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        result = service.request_lecturer_assistance(
            session_id=session.session_id,
            user_id="host_123",
            message="Need help with recursion",
        )

        assert result is True
        assert session.lecturer_assistance is True

    def test_request_assistance_nonexistent_session(self):
        """Test requesting assistance for non-existent session."""
        service = CollaborationService()

        result = service.request_lecturer_assistance(
            session_id="nonexistent",
            user_id="user_123",
        )

        assert result is False


class TestSessionInfo:
    """Test suite for session information retrieval."""

    def test_get_session_info(self):
        """Test getting session information."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
            title="Test Session",
        )

        info = service.get_session_info(session.session_id)

        assert info is not None
        assert info["session_id"] == session.session_id
        assert info["title"] == "Test Session"
        assert info["host_id"] == "host_123"
        assert "participants" in info
        assert "code_content" in info

    def test_get_session_info_nonexistent(self):
        """Test getting info for non-existent session."""
        service = CollaborationService()

        info = service.get_session_info("nonexistent")

        assert info is None


class TestPublicSessions:
    """Test suite for public session listing."""

    def test_get_public_sessions_empty(self):
        """Test getting public sessions when none exist."""
        service = CollaborationService()

        sessions = service.get_public_sessions()

        assert isinstance(sessions, list)

    def test_get_public_sessions_filters_private(self):
        """Test that private sessions are filtered out."""
        service = CollaborationService()

        # Create private session
        service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
            is_public=False,
        )

        sessions = service.get_public_sessions()

        assert len(sessions) == 0

    def test_get_public_sessions_includes_public(self):
        """Test that public sessions are included."""
        service = CollaborationService()

        service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
            is_public=True,
        )

        sessions = service.get_public_sessions()

        assert len(sessions) == 1
        assert sessions[0]["host_name"] == "Host"


class TestSessionRecording:
    """Test suite for session recording functionality."""

    def test_get_session_recording_nonexistent(self):
        """Test getting recording for non-existent session."""
        service = CollaborationService()

        recording = service.get_session_recording("nonexistent")

        assert recording is None

    def test_session_events_recorded(self):
        """Test that session events are recorded."""
        service = CollaborationService()

        session = service.create_session(
            host_id="host_123",
            username="Host",
            assignment_id="assign_001",
        )

        service.join_session(
            session_id=session.session_id,
            user_id="user_456",
            username="Participant",
        )

        # Apply a code change (which records events)
        service.apply_code_change(
            user_id="host_123",
            change_data={
                "operation": "insert",
                "position": 0,
                "content": "test",
            },
        )

        recording = service.get_session_recording(session.session_id)

        assert recording is not None
        assert "events" in recording
        assert len(recording["events"]) > 0


class TestWebSocketManagement:
    """Test suite for WebSocket connection management."""

    def test_register_websocket(self):
        """Test registering a WebSocket connection."""
        service = CollaborationService()

        mock_websocket = object()
        service.register_websocket("user_123", mock_websocket)

        assert "user_123" in service.websocket_connections
        assert service.websocket_connections["user_123"] is mock_websocket

    def test_unregister_websocket(self):
        """Test unregistering a WebSocket connection."""
        service = CollaborationService()

        mock_websocket = object()
        service.register_websocket("user_123", mock_websocket)
        service.unregister_websocket("user_123")

        assert "user_123" not in service.websocket_connections

    def test_unregister_nonexistent_websocket(self):
        """Test unregistering non-existent WebSocket."""
        service = CollaborationService()

        # Should not raise an error
        service.unregister_websocket("nonexistent")

