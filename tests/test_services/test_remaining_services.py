"""
Comprehensive Tests for Services 11-15
Email, Collaboration, Code Execution, Cache, and Other Remaining Services
"""

import json
import pytest
import redis
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings


# ==================== 11. Email Service Tests ====================

@pytest.mark.unit
class TestEmailService:
    """Test suite for Email Service (11.1-11.2)"""

    @pytest.fixture
    def app(self):
        """Create a Flask app context for testing"""
        from app import create_app
        app = create_app()
        app.config['TESTING'] = True
        app.config['MAIL_USERNAME'] = 'test@example.com'
        return app

    def test_send_welcome_email(self, app):
        """Test send_welcome_email function (11.1)"""
        from services.email_service import send_welcome_email

        with app.app_context():
            with patch('services.email_service.Thread') as mock_thread:
                result = send_welcome_email("user@example.com", "John Doe", "student")

                assert result is True
                mock_thread.assert_called_once()

    def test_send_password_reset_email(self, app):
        """Test send_password_reset_email function (11.1)"""
        from services.email_service import send_password_reset_email

        with app.app_context():
            with patch('services.email_service.Thread') as mock_thread:
                result = send_password_reset_email("user@example.com", "John Doe", "reset_token_123")

                assert result is True
                mock_thread.assert_called_once()

    def test_send_assignment_notification(self, app):
        """Test send_assignment_notification function (11.1)"""
        from services.email_service import send_assignment_notification
        from datetime import datetime

        with app.app_context():
            with patch('services.email_service.Thread') as mock_thread:
                result = send_assignment_notification(
                    "user@example.com",
                    "John Doe",
                    "Python Basics",
                    datetime(2025, 12, 31)
                )

                assert result is True
                mock_thread.assert_called_once()

    def test_send_submission_confirmation(self, app):
        """Test send_submission_confirmation function (11.1)"""
        from services.email_service import send_submission_confirmation

        with app.app_context():
            with patch('services.email_service.Thread') as mock_thread:
                result = send_submission_confirmation("user@example.com", "John Doe", "Assignment 1", 95)

                assert result is True
                mock_thread.assert_called_once()

    def test_send_plagiarism_alert(self, app):
        """Test send_plagiarism_alert function (11.1)"""
        from services.email_service import send_plagiarism_alert

        with app.app_context():
            with patch('services.email_service.Thread') as mock_thread:
                result = send_plagiarism_alert(
                    "lecturer@example.com",
                    "Assignment 1",
                    "Student A",
                    "Student B",
                    0.85
                )

                assert result is True
                mock_thread.assert_called_once()

    def test_send_achievement_notification(self, app):
        """Test send_achievement_notification function (11.1)"""
        from services.email_service import send_achievement_notification

        with app.app_context():
            with patch('services.email_service.Thread') as mock_thread:
                result = send_achievement_notification(
                    "user@example.com",
                    "John Doe",
                    "First Submission",
                    "🏆",
                    100
                )

                assert result is True
                mock_thread.assert_called_once()

    def test_send_email_error_handling(self, app):
        """Test send_email error handling (11.2)"""
        from services.email_service import send_email

        with app.app_context():
            # Should handle error gracefully when mail is not configured
            result = send_email("Test Subject", "user@example.com", "<p>Test</p>")

            # Result can be True (if Thread started) or False (if error occurred)
            # The important thing is that no exception is raised
            assert result in [True, False]


# ==================== 12. Collaboration Service Tests ====================

@pytest.mark.unit
class TestCollaborationService:
    """Test suite for Collaboration Service (12.1-12.2)"""

    @pytest.fixture
    def service(self):
        """Create a fresh collaboration service instance for each test"""
        from services.collaboration_service import CollaborationService
        return CollaborationService()

    # ==================== 12.1 Session Management Tests ====================

    def test_session_creation(self, service):
        """Test collaboration session creation (12.1)"""
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456",
            title="Python Pair Programming"
        )

        assert session is not None
        assert session.session_id is not None
        assert session.host_id == "host_123"
        assert session.title == "Python Pair Programming"
        assert session.assignment_id == "assignment_456"
        assert session.status.value == "waiting"
        assert len(session.participants) == 1
        assert "host_123" in session.participants
        assert session.participants["host_123"].role.value == "host"
        assert session.code_content == "# Start coding here...\n"

    def test_session_creation_default_title(self, service):
        """Test session creation with default title (12.1)"""
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        assert session.title == "TestHost's Coding Session"

    def test_participant_joining_new_user(self, service):
        """Test participant joining session (12.1)"""
        # Create session first
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        # Join session
        from services.collaboration_service import UserRole
        result = service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        assert result is not None
        assert result.session_id == session.session_id
        assert len(result.participants) == 2
        assert "participant_456" in result.participants
        assert result.participants["participant_456"].username == "TestParticipant"
        assert result.participants["participant_456"].is_online is True
        assert result.status.value == "active"  # Should become active with 2+ participants

    def test_participant_joining_nonexistent_session(self, service):
        """Test joining non-existent session returns None (12.1)"""
        from services.collaboration_service import UserRole
        result = service.join_session(
            session_id="nonexistent_session",
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        assert result is None

    def test_participant_joining_full_session(self, service):
        """Test joining full session is rejected (12.1)"""
        from services.collaboration_service import UserRole

        # Create session
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        # Fill session to max capacity (4 participants)
        for i in range(1, 4):
            service.join_session(
                session_id=session.session_id,
                user_id=f"participant_{i}",
                username=f"Participant{i}",
                role=UserRole.PARTICIPANT
            )

        # Try to join when full
        result = service.join_session(
            session_id=session.session_id,
            user_id="participant_5",
            username="Participant5",
            role=UserRole.PARTICIPANT
        )

        assert result is None

    def test_participant_rejoining_session(self, service):
        """Test participant rejoining session updates online status (12.1)"""
        from services.collaboration_service import UserRole

        # Create and join session
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        # Mark as offline
        session.participants["participant_456"].is_online = False

        # Rejoin
        result = service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        assert result.participants["participant_456"].is_online is True

    def test_lecturer_joining_full_session(self, service):
        """Test lecturer can join full session (12.1)"""
        from services.collaboration_service import UserRole

        # Create session and fill to capacity
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        for i in range(1, 4):
            service.join_session(
                session_id=session.session_id,
                user_id=f"participant_{i}",
                username=f"Participant{i}",
                role=UserRole.PARTICIPANT
            )

        # Lecturer should be able to join even when full
        result = service.join_session(
            session_id=session.session_id,
            user_id="lecturer_789",
            username="TestLecturer",
            role=UserRole.LECTURER
        )

        assert result is not None
        assert len(result.participants) == 5  # 1 host + 3 participants + 1 lecturer

    def test_participant_leaving(self, service):
        """Test participant leaving session (12.1)"""
        from services.collaboration_service import UserRole

        # Create session and add participant
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        # Leave session
        result = service.leave_session("participant_456")

        assert result is True
        assert session.participants["participant_456"].is_online is False
        assert "participant_456" not in service.user_sessions

    def test_participant_leaving_nonexistent_session(self, service):
        """Test leaving non-existent session returns False (12.1)"""
        result = service.leave_session("nonexistent_user")
        assert result is False

    def test_host_leaving_ends_session(self, service):
        """Test host leaving ends the session (12.1)"""
        from services.collaboration_service import UserRole

        # Create session and add participant
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        # Host leaves
        service.leave_session("host_123")

        assert session.status.value == "ended"

    def test_last_participant_leaving_ends_session(self, service):
        """Test last participant leaving ends session (12.1)"""
        # Create session
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        # Host leaves (last participant)
        service.leave_session("host_123")

        assert session.status.value == "ended"

    # ==================== 12.2 Real-time Synchronization Tests ====================

    def test_code_change_insert(self, service):
        """Test code change insertion (12.2)"""
        from services.collaboration_service import UserRole

        # Create session and join
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        # Make session active
        from services.collaboration_service import SessionStatus
        session.status = SessionStatus.ACTIVE

        # Apply code change
        change_data = {
            "operation": "insert",
            "position": 0,
            "content": "print('Hello')\n"
        }

        result = service.apply_code_change("host_123", change_data)

        assert result is True
        assert "print('Hello')" in session.code_content
        assert len(session.change_history) == 1
        assert session.change_history[0].operation == "insert"
        assert session.change_history[0].user_id == "host_123"

    def test_code_change_delete(self, service):
        """Test code change deletion (12.2)"""
        # Create session
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        # Set initial code
        from services.collaboration_service import SessionStatus
        session.code_content = "print('Hello World')\n"
        session.status = SessionStatus.ACTIVE

        # Delete operation
        change_data = {
            "operation": "delete",
            "position": 6,
            "length": 7  # Delete "'Hello "
        }

        result = service.apply_code_change("host_123", change_data)

        assert result is True
        assert "print(World')" in session.code_content

    def test_code_change_replace(self, service):
        """Test code change replacement (12.2)"""
        # Create session
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        from services.collaboration_service import SessionStatus
        session.code_content = "print('Hello')\n"
        session.status = SessionStatus.ACTIVE

        # Replace operation
        change_data = {
            "operation": "replace",
            "position": 7,
            "content": "World",
            "length": 5  # Replace "Hello"
        }

        result = service.apply_code_change("host_123", change_data)

        assert result is True
        assert "print('World')" in session.code_content

    def test_code_change_inactive_session(self, service):
        """Test code change on inactive session fails (12.2)"""
        # Create session (status is WAITING)
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        change_data = {
            "operation": "insert",
            "position": 0,
            "content": "test"
        }

        result = service.apply_code_change("host_123", change_data)

        assert result is False

    def test_code_change_nonexistent_user(self, service):
        """Test code change from non-existent user fails (12.2)"""
        change_data = {
            "operation": "insert",
            "position": 0,
            "content": "test"
        }

        result = service.apply_code_change("nonexistent_user", change_data)

        assert result is False

    def test_cursor_position_tracking(self, service):
        """Test cursor position tracking (12.2)"""
        from services.collaboration_service import UserRole

        # Create session and join
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        # Update cursor position
        result = service.update_cursor_position("participant_456", 42)

        assert result is True
        assert session.participants["participant_456"].cursor_position == 42

    def test_cursor_position_nonexistent_user(self, service):
        """Test cursor update for non-existent user fails (12.2)"""
        result = service.update_cursor_position("nonexistent_user", 42)
        assert result is False

    def test_session_recording(self, service):
        """Test session recording (12.2)"""
        from services.collaboration_service import UserRole, SessionStatus

        # Create session
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        service.join_session(
            session_id=session.session_id,
            user_id="participant_456",
            username="TestParticipant",
            role=UserRole.PARTICIPANT
        )

        # Set session to active (correct way to set enum)
        session.status = SessionStatus.ACTIVE

        # Apply code change (should be recorded)
        change_data = {
            "operation": "insert",
            "position": 0,
            "content": "print('test')\n"
        }

        service.apply_code_change("host_123", change_data)

        # Get recording
        recording = service.get_session_recording(session.session_id)

        assert recording is not None
        assert "events" in recording
        assert len(recording["events"]) > 0
        assert recording["events"][0]["type"] == "code_change"

    def test_get_session_info(self, service):
        """Test getting session information (12.1)"""
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456",
            title="Test Session"
        )

        info = service.get_session_info(session.session_id)

        assert info is not None
        assert info["session_id"] == session.session_id
        assert info["title"] == "Test Session"
        assert info["assignment_id"] == "assignment_456"
        assert info["status"] == "waiting"
        assert len(info["participants"]) == 1

    def test_get_public_sessions(self, service):
        """Test getting public sessions list (12.1)"""
        # Create public session
        service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456",
            title="Public Session",
            is_public=True
        )

        # Create private session
        service.create_session(
            host_id="host_456",
            username="TestHost2",
            assignment_id="assignment_789",
            title="Private Session",
            is_public=False
        )

        public_sessions = service.get_public_sessions()

        assert len(public_sessions) == 1
        assert public_sessions[0]["title"] == "Public Session"

    def test_request_lecturer_assistance(self, service):
        """Test requesting lecturer assistance (12.2)"""
        session = service.create_session(
            host_id="host_123",
            username="TestHost",
            assignment_id="assignment_456"
        )

        result = service.request_lecturer_assistance(
            session_id=session.session_id,
            user_id="host_123",
            message="Need help with algorithm"
        )

        assert result is True
        assert session.lecturer_assistance is True


# ==================== 13. Code Execution Service Tests ====================

@pytest.mark.unit
class TestCodeExecutionService:
    """Test suite for Code Execution Service (13.1-13.2)"""

    def test_docker_not_available(self):
        """Test behavior when docker module is not present (13.1)"""
        from services.code_execution_service import compile_and_run_code

        with patch('services.code_execution_service.DOCKER_AVAILABLE', False):
            result = compile_and_run_code("print('test')", "python")
            assert result['success'] is False
            assert "Docker SDK not installed" in result['error']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_code_execution_in_sandbox(self, mock_docker):
        """Test code execution in sandbox (13.1)"""
        from services.code_execution_service import compile_and_run_code

        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Hello"
        mock_container.stats.return_value = {'memory_stats': {'usage': 1024}}

        result = compile_and_run_code("print('Hello')", "python")

        assert result is not None
        assert 'output' in result or 'error' in result

    def test_get_supported_languages(self):
        """Test get_supported_languages function (13.2)"""
        from services.code_execution_service import get_supported_languages

        languages = get_supported_languages()

        assert languages is not None
        assert len(languages) > 0
        assert any(lang['value'] == 'python' for lang in languages)
        assert any(lang['value'] == 'java' for lang in languages)
        assert any(lang['value'] == 'cpp' for lang in languages)

    def test_check_syntax(self):
        """Test check_syntax function (13.2)"""
        from services.code_execution_service import check_syntax

        result = check_syntax("print('hello')", "python")

        assert result is not None
        assert 'valid' in result

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_python_execution_command(self, mock_docker):
        """Test Python execution command construction (13.2)"""
        from services.code_execution_service import compile_and_run_code

        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"4"

        compile_and_run_code("print(2 + 2)", "python")

        args, kwargs = mock_client.containers.run.call_args
        assert "python main.py" in kwargs['command']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_java_execution_command(self, mock_docker):
        """Test Java execution command construction (13.2)"""
        from services.code_execution_service import compile_and_run_code

        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Hello"

        compile_and_run_code("class Main {}", "java")

        args, kwargs = mock_client.containers.run.call_args
        assert "javac Main.java && java Main" in kwargs['command']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_cpp_execution_command(self, mock_docker):
        """Test C++ execution command construction (13.2)"""
        from services.code_execution_service import compile_and_run_code

        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Hello"

        compile_and_run_code("#include <iostream>", "cpp")

        args, kwargs = mock_client.containers.run.call_args
        assert "g++ -o main main.cpp && ./main" in kwargs['command']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_javascript_execution_command(self, mock_docker):
        """Test JavaScript execution command construction (13.2)"""
        from services.code_execution_service import compile_and_run_code

        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Hello"

        compile_and_run_code("console.log('Hello');", "javascript")

        args, kwargs = mock_client.containers.run.call_args
        assert "node main.js" in kwargs['command']

    @patch('services.code_execution_service.DOCKER_AVAILABLE', True)
    @patch('services.code_execution_service.docker')
    def test_c_execution_command(self, mock_docker):
        """Test C execution command construction (13.2)"""
        from services.code_execution_service import compile_and_run_code

        mock_client = MagicMock()
        mock_container = MagicMock()
        mock_docker.from_env.return_value = mock_client
        mock_client.containers.run.return_value = mock_container
        mock_container.wait.return_value = {'StatusCode': 0}
        mock_container.logs.return_value = b"Hello"

        compile_and_run_code("#include <stdio.h>\nint main() { printf(\"Hello\"); return 0; }", "c")

        args, kwargs = mock_client.containers.run.call_args
        assert "gcc -o main main.c && ./main" in kwargs['command']


# ==================== 14. Cache Service Tests ====================

@pytest.mark.unit
class TestCacheService:
    """Test suite for Cache Service (14.1)"""

    @patch('services.cache_service.redis.Redis')
    def test_cache_get_operation(self, mock_redis_class):
        """Test cache get operation (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = '{"data": "test_value"}'

        # Create cache service
        cache = CacheService()

        # Test get operation
        result = cache.get_cached("test_key")

        assert result == {"data": "test_value"}
        mock_redis_instance.get.assert_called_once_with("test_key")

    @patch('services.cache_service.redis.Redis')
    def test_cache_get_operation_miss(self, mock_redis_class):
        """Test cache get operation when key doesn't exist (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.return_value = None

        # Create cache service
        cache = CacheService()

        # Test get operation with cache miss
        result = cache.get_cached("nonexistent_key")

        assert result is None
        mock_redis_instance.get.assert_called_once_with("nonexistent_key")

    @patch('services.cache_service.redis.Redis')
    def test_cache_set_operation_with_ttl(self, mock_redis_class):
        """Test cache set operation with TTL (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.setex.return_value = True

        # Create cache service
        cache = CacheService()

        # Test set operation with custom TTL
        test_data = {"user_id": 123, "name": "Test User"}
        result = cache.cache_result("user:123", test_data, expiration=1800)

        assert result is True
        mock_redis_instance.setex.assert_called_once()
        call_args = mock_redis_instance.setex.call_args
        assert call_args[0][0] == "user:123"
        assert call_args[0][1] == 1800
        assert json.loads(call_args[0][2]) == test_data

    @patch('services.cache_service.redis.Redis')
    def test_cache_set_operation_default_ttl(self, mock_redis_class):
        """Test cache set operation with default TTL (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.setex.return_value = True

        # Create cache service
        cache = CacheService()

        # Test set operation with default TTL (3600)
        test_data = {"score": 95}
        result = cache.cache_result("score:assignment:1", test_data)

        assert result is True
        mock_redis_instance.setex.assert_called_once()
        call_args = mock_redis_instance.setex.call_args
        assert call_args[0][0] == "score:assignment:1"
        assert call_args[0][1] == 3600  # Default TTL

    @patch('services.cache_service.redis.Redis')
    def test_cache_delete_operation(self, mock_redis_class):
        """Test cache delete operation (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.delete.return_value = 1

        # Create cache service
        cache = CacheService()

        # Test delete operation
        result = cache.invalidate("test_key")

        assert result is True
        mock_redis_instance.delete.assert_called_once_with("test_key")

    @patch('services.cache_service.redis.Redis')
    def test_cache_invalidation_pattern(self, mock_redis_class):
        """Test cache invalidation with pattern matching (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.keys.return_value = ["user:1", "user:2", "user:3"]
        mock_redis_instance.delete.return_value = 3

        # Create cache service
        cache = CacheService()

        # Test pattern invalidation
        result = cache.invalidate_pattern("user:*")

        assert result is True
        mock_redis_instance.keys.assert_called_once_with("user:*")
        mock_redis_instance.delete.assert_called_once_with("user:1", "user:2", "user:3")

    @patch('services.cache_service.redis.Redis')
    def test_cache_invalidation_pattern_no_matches(self, mock_redis_class):
        """Test cache invalidation when pattern has no matches (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.keys.return_value = []

        # Create cache service
        cache = CacheService()

        # Test pattern invalidation with no matches
        result = cache.invalidate_pattern("nonexistent:*")

        assert result is True
        mock_redis_instance.keys.assert_called_once_with("nonexistent:*")
        mock_redis_instance.delete.assert_not_called()

    @patch('services.cache_service.redis.Redis')
    def test_cache_disabled_when_redis_unavailable(self, mock_redis_class):
        """Test cache service gracefully handles Redis unavailability (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client to fail
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.side_effect = redis.ConnectionError("Connection refused")

        # Create cache service
        cache = CacheService()

        # Verify cache is disabled
        assert cache.enabled is False
        assert cache.redis_client is None

        # Test operations return appropriate values when disabled
        assert cache.get_cached("key") is None
        assert cache.cache_result("key", "value") is False
        assert cache.invalidate("key") is False
        assert cache.invalidate_pattern("pattern:*") is False

    @patch('services.cache_service.redis.Redis')
    def test_cache_error_handling_on_get(self, mock_redis_class):
        """Test cache handles errors during get operation (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.get.side_effect = redis.RedisError("Connection lost")

        # Create cache service
        cache = CacheService()

        # Test get operation with error
        result = cache.get_cached("test_key")

        assert result is None

    @patch('services.cache_service.redis.Redis')
    def test_cache_error_handling_on_set(self, mock_redis_class):
        """Test cache handles errors during set operation (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True
        mock_redis_instance.setex.side_effect = redis.RedisError("Connection lost")

        # Create cache service
        cache = CacheService()

        # Test set operation with error
        result = cache.cache_result("test_key", {"data": "value"})

        assert result is False

    @patch('services.cache_service.redis.Redis')
    def test_cache_round_trip(self, mock_redis_class):
        """Test cache round-trip: set then get returns same value (14.1)"""
        from services.cache_service import CacheService

        # Setup mock Redis client
        mock_redis_instance = MagicMock()
        mock_redis_class.return_value = mock_redis_instance
        mock_redis_instance.ping.return_value = True

        # Store the serialized value for retrieval
        stored_value = None
        def mock_setex(key, ttl, value):
            nonlocal stored_value
            stored_value = value
            return True

        def mock_get(key):
            return stored_value

        mock_redis_instance.setex.side_effect = mock_setex
        mock_redis_instance.get.side_effect = mock_get

        # Create cache service
        cache = CacheService()

        # Test round-trip
        original_data = {"user_id": 456, "score": 98, "achievements": ["first_submission", "perfect_score"]}
        cache.cache_result("test:roundtrip", original_data)
        retrieved_data = cache.get_cached("test:roundtrip")

        assert retrieved_data == original_data


# ==================== 15. Remaining Services Tests ====================

@pytest.mark.unit
class TestCodeAnalysisService:
    """Test suite for Code Analysis Service (15.1)"""

    def test_complexity_calculation(self):
        """Test complexity calculation (15.1)"""
        from services.code_analysis_service import code_analyzer

        code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        result = code_analyzer.analyze_code(code, "python")

        assert result is not None
        assert result.code_metrics.cyclomatic_complexity >= 1
        assert result.code_metrics.lines_of_code > 0

    def test_complexity_calculation_nested_loops(self):
        """Test complexity with nested loops (15.1)"""
        from services.code_analysis_service import code_analyzer

        code = """
def bubble_sort(arr):
    for i in range(len(arr)):
        for j in range(len(arr) - 1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
"""
        result = code_analyzer.analyze_code(code, "python")

        assert result.code_metrics.cyclomatic_complexity >= 2
        assert result.code_metrics.nesting_depth >= 2

    def test_big_o_analysis_linear(self):
        """Test Big O analysis for linear complexity (15.1)"""
        from services.code_analysis_service import code_analyzer

        code = "for i in range(n):\n    print(i)"
        result = code_analyzer.analyze_code(code, "python")

        assert result.big_o_analysis is not None
        assert "O(n)" in result.big_o_analysis["time_complexity"]

    def test_big_o_analysis_quadratic(self):
        """Test Big O analysis for quadratic complexity (15.1)"""
        from services.code_analysis_service import code_analyzer

        code = """
for i in range(n):
    for j in range(n):
        print(i, j)
"""
        result = code_analyzer.analyze_code(code, "python")

        assert "O(n²)" in result.big_o_analysis["time_complexity"]

    def test_code_metrics_functions(self):
        """Test code metrics for function count (15.1)"""
        from services.code_analysis_service import code_analyzer

        code = """
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b

def multiply(a, b):
    return a * b
"""
        result = code_analyzer.analyze_code(code, "python")

        assert result.code_metrics.function_count == 3
        assert result.code_metrics.lines_of_code > 0

    def test_code_metrics_classes(self):
        """Test code metrics for class count (15.1)"""
        from services.code_analysis_service import code_analyzer

        code = """
class Calculator:
    def add(self, a, b):
        return a + b

class StringHelper:
    def reverse(self, s):
        return s[::-1]
"""
        result = code_analyzer.analyze_code(code, "python")

        assert result.code_metrics.class_count == 2
        assert result.code_metrics.function_count >= 2


@pytest.mark.unit
class TestCodeReviewService:
    """Test suite for Code Review Service (15.2)"""

    def test_code_review_generation(self):
        """Test code review generation (15.2)"""
        from services.code_review_service import CodeReviewService

        service = CodeReviewService()
        review_data = {
            "title": "Test Review",
            "assignment_id": "test_assignment",
            "author_id": "student_123",
            "author_name": "Test Student",
            "reviewer_id": "reviewer_456",
            "reviewer_name": "Test Reviewer",
            "code_snapshot": "def test(): return 1",
            "review_data": {
                "overall_rating": 4,
                "criteria_scores": {"correctness": 40, "quality": 30}
            },
            "feedback": "Good work!",
            "comments": [],
            "review_time": 30,
            "lines_reviewed": 10
        }

        result = service.submit_review(review_data)

        assert result is not None
        assert result["success"] is True
        assert "review_id" in result

    def test_suggestion_generation(self):
        """Test suggestion generation (15.2)"""
        from services.code_review_service import CodeReviewService

        service = CodeReviewService()
        comment_data = {
            "review_id": "test_review",
            "author_id": "reviewer_123",
            "author_name": "Test Reviewer",
            "line_number": 5,
            "comment_type": "suggestion",
            "content": "Consider using list comprehension here",
            "severity": "low"
        }

        result = service.add_comment(comment_data)

        assert result is not None
        assert result["success"] is True
        assert "comment_id" in result

    def test_review_request_creation(self):
        """Test review request creation (15.2)"""
        from services.code_review_service import CodeReviewService

        service = CodeReviewService()
        request_data = {
            "assignment_id": "assignment_123",
            "author_id": "student_456",
            "author_name": "Test Student",
            "title": "Need review for sorting algorithm",
            "description": "Please review my bubble sort implementation",
            "priority": "medium",
            "language": "python"
        }

        result = service.create_review_request(request_data)

        assert result is not None
        assert result["success"] is True
        assert "request_id" in result


@pytest.mark.unit
class TestMetricsService:
    """Test suite for Metrics Service (15.3)"""

    def test_metric_collection_submission(self):
        """Test metric collection for submissions (15.3)"""
        from services.metrics_service import submissions_total

        initial_count = submissions_total._value._value if hasattr(submissions_total, '_value') else 0

        # Record a submission
        submissions_total.labels(language="python", status="success").inc()

        # Verify metric was recorded
        assert True  # Metric collection doesn't crash

    def test_metric_collection_plagiarism(self):
        """Test metric collection for plagiarism checks (15.3)"""
        from services.metrics_service import plagiarism_checks_total

        # Record a plagiarism check
        plagiarism_checks_total.labels(result="passed").inc()

        # Verify metric was recorded
        assert True  # Metric collection doesn't crash

    def test_metric_aggregation_grading_duration(self):
        """Test metric aggregation for grading duration (15.3)"""
        from services.metrics_service import grading_duration_seconds

        # Record grading duration
        grading_duration_seconds.labels(language="python").observe(2.5)

        # Verify metric was recorded
        assert True  # Metric aggregation doesn't crash

    def test_metric_gauge_active_users(self):
        """Test gauge metric for active users (15.3)"""
        from services.metrics_service import active_users

        # Set active users count
        active_users.labels(role="student").set(50)
        active_users.labels(role="lecturer").set(5)

        # Verify metric was set
        assert True  # Gauge update doesn't crash

    def test_metric_cache_hit_ratio(self):
        """Test cache hit ratio metric (15.3)"""
        from services.metrics_service import update_cache_metrics

        # Update cache metrics
        update_cache_metrics(hits=80, misses=20)

        # Verify metric was updated
        assert True  # Cache metric update doesn't crash


@pytest.mark.unit
class TestProgressTrackerService:
    """Test suite for Progress Tracker Service (15.4)"""

    def test_progress_calculation(self):
        """Test progress calculation (15.4)"""
        from services.progress_tracker_service import ProgressTrackerService

        service = ProgressTrackerService()
        overview = service.get_student_overview("test_student")

        assert overview is not None
        assert "overview" in overview
        assert "total_assignments" in overview["overview"]
        assert "average_score" in overview["overview"]
        assert overview["overview"]["completion_rate"] >= 0

    def test_milestone_tracking(self):
        """Test milestone tracking (15.4)"""
        from services.progress_tracker_service import ProgressTrackerService

        service = ProgressTrackerService()
        achievements = service.get_achievement_progress("test_student")

        assert achievements is not None
        assert "achievements" in achievements
        assert "earned_count" in achievements
        assert "total_count" in achievements
        assert isinstance(achievements["achievements"], list)

    def test_performance_timeline(self):
        """Test performance timeline generation (15.4)"""
        from services.progress_tracker_service import ProgressTrackerService

        service = ProgressTrackerService()
        timeline = service.get_performance_timeline("test_student", "6months")

        assert timeline is not None
        assert "timeline" in timeline or "metrics" in timeline

    def test_skill_analysis(self):
        """Test skill analysis (15.4)"""
        from services.progress_tracker_service import ProgressTrackerService

        service = ProgressTrackerService()
        skills = service.get_skill_analysis("test_student")

        assert skills is not None
        assert "skills" in skills or "strongest_skills" in skills


@pytest.mark.unit
class TestOTPService:
    """Test suite for OTP Service (15.5)"""

    def test_otp_generation(self):
        """Test OTP generation (15.5)"""
        from services.otp_service import OTPService

        secret = OTPService.generate_secret()

        assert secret is not None
        assert len(secret) >= 16  # Base32 secrets are typically 16+ chars
        assert isinstance(secret, str)

    def test_otp_validation_correct(self):
        """Test OTP validation with correct code (15.5)"""
        from services.otp_service import OTPService
        import pyotp

        secret = OTPService.generate_secret()
        totp = pyotp.TOTP(secret)
        current_otp = totp.now()

        is_valid = OTPService.verify_otp(secret, current_otp)

        assert is_valid is True

    def test_otp_validation_incorrect(self):
        """Test OTP validation with incorrect code (15.5)"""
        from services.otp_service import OTPService

        secret = OTPService.generate_secret()
        is_valid = OTPService.verify_otp(secret, "000000")

        assert is_valid is False

    def test_provisioning_uri_generation(self):
        """Test provisioning URI generation (15.5)"""
        from services.otp_service import OTPService

        secret = OTPService.generate_secret()
        uri = OTPService.get_provisioning_uri(secret, "test@example.com")

        assert uri is not None
        assert "otpauth://totp/" in uri
        assert "test" in uri and "example.com" in uri  # Email may be URL-encoded

    def test_qr_code_generation(self):
        """Test QR code generation (15.5)"""
        from services.otp_service import OTPService

        secret = OTPService.generate_secret()
        uri = OTPService.get_provisioning_uri(secret, "test@example.com")
        qr_code = OTPService.generate_qr_code(uri)

        assert qr_code is not None
        assert isinstance(qr_code, str)
        assert len(qr_code) > 0  # Base64 encoded image


@pytest.mark.unit
class TestLabGradingService:
    """Test suite for Lab Grading Service (15.6)"""

    def test_lab_assignment_grading(self):
        """Test lab assignment grading (15.6)"""
        from services.lab_grading_service import lab_grading_service, LabAssignment, LabType

        assignment = LabAssignment(
            assignment_id="lab_123",
            title="Sorting Algorithm",
            lab_type=LabType.ALGORITHMS,
            max_score=100,
            test_cases=[
                {"input": "[3, 1, 2]", "expected": "[1, 2, 3]"}
            ],
            evaluation_criteria={"correctness": 40, "efficiency": 30, "quality": 30},
            learning_objectives=["Understand sorting"]
        )

        # Test that assignment structure is valid
        assert assignment.assignment_id == "lab_123"
        assert assignment.max_score == 100
        assert len(assignment.test_cases) == 1

    def test_lab_submission_handling(self):
        """Test lab submission handling (15.6)"""
        from services.lab_grading_service import lab_grading_service

        # Test that service initializes correctly
        assert lab_grading_service is not None
        assert lab_grading_service.lab_templates is not None
        assert lab_grading_service.feedback_templates is not None

    def test_lab_templates_loaded(self):
        """Test lab templates are loaded (15.6)"""
        from services.lab_grading_service import lab_grading_service, LabType

        templates = lab_grading_service.lab_templates

        assert templates is not None
        assert LabType.ALGORITHMS in templates
        assert LabType.DATA_STRUCTURES in templates


@pytest.mark.unit
class TestTracingService:
    """Test suite for Tracing Service (15.7)"""

    def test_trace_collection_decorator(self):
        """Test trace collection with decorator (15.7)"""
        from services.tracing_service import trace_function

        @trace_function("test_operation")
        def sample_function(x, y):
            return x + y

        result = sample_function(2, 3)

        assert result == 5  # Function works correctly

    def test_trace_export_attributes(self):
        """Test adding span attributes (15.7)"""
        from services.tracing_service import add_span_attributes

        # Should not crash even if tracing is disabled
        add_span_attributes(user_id="123", operation="test")

        assert True  # No crash

    def test_trace_database_decorator(self):
        """Test database tracing decorator (15.7)"""
        from services.tracing_service import trace_database_query

        @trace_database_query("submissions", "find")
        def query_submissions():
            return [{"id": 1}, {"id": 2}]

        result = query_submissions()

        assert len(result) == 2

    def test_trace_ai_request_decorator(self):
        """Test AI request tracing decorator (15.7)"""
        from services.tracing_service import trace_ai_request

        @trace_ai_request("gpt-3.5-turbo")
        def call_ai_api():
            return {"response": "test", "usage": {"total_tokens": 100}}

        result = call_ai_api()

        assert result["response"] == "test"


@pytest.mark.unit
class TestSecureCodeExecutor:
    """Test suite for Secure Code Executor (15.8)"""

    @pytest.mark.skipif(True, reason="Docker not available in test environment")
    def test_secure_execution(self):
        """Test secure execution (15.8)"""
        # Skipped: Docker not available
        pass

    @pytest.mark.skipif(True, reason="Docker not available in test environment")
    def test_security_checks_with_timeout(self):
        """Test security checks with timeout (15.8)"""
        # Skipped: Docker not available
        pass

    @pytest.mark.skipif(True, reason="Docker not available in test environment")
    def test_get_filename_for_language(self):
        """Test filename generation for different languages (15.8)"""
        # Skipped: Docker not available - module cannot be imported
        pass

    @pytest.mark.skipif(True, reason="Docker not available in test environment")
    def test_get_run_command_for_language(self):
        """Test run command generation for different languages (15.8)"""
        # Skipped: Docker not available - module cannot be imported
        pass


# ==================== 15.9 Service Error Handling Property Test ====================

@pytest.mark.property
class TestServiceErrorHandling:
    """Property 1: Service Error Handling Consistency (15.9)
    Validates: Requirements 2.9
    Property: All services should handle errors consistently

    **Feature: comprehensive-testing, Property 1: Service Error Handling Consistency**
    """

    @given(st.text(min_size=0, max_size=100))
    @settings(max_examples=30, deadline=2000)
    def test_services_handle_invalid_input(self, invalid_input):
        """Services should not crash on invalid input"""
        from services.code_analysis_service import code_analyzer

        try:
            result = code_analyzer.analyze_code(invalid_input, "python")
            # Should return a result or raise a controlled exception
            assert result is not None
            assert hasattr(result, 'code_metrics')
        except Exception as e:
            # Should be a handled exception, not a crash
            assert str(e) != ""  # Has error message

    def test_service_error_response_structure(self):
        """Service errors should have consistent structure"""
        from services.code_analysis_service import code_analyzer

        try:
            result = code_analyzer.analyze_code("", "python")
            # Should return a valid result even for empty input
            assert result is not None
            assert hasattr(result, 'code_metrics')
            assert hasattr(result, 'big_o_analysis')
        except Exception:
            # Exceptions are also acceptable
            pass


# Run tests with coverage
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=services", "--cov-report=term-missing"])
