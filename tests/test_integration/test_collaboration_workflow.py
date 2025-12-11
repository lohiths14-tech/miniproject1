"""
Integration tests for collaboration session workflow
Tests end-to-end flow: create → join → code sync → recording → replay
**Validates: Requirements 4.6**
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from datetime import datetime
from services.collaboration_service import collaboration_service, UserRole

@pytest.mark.integration
class TestCollaborationWorkflow:
    """Test complete collaboration session workflow"""

    def setup_method(self):
        """Reset collaboration service before each test"""
        collaboration_service.active_sessions = {}
        collaboration_service.user_sessions = {}
        collaboration_service.websocket_connections = {}
        collaboration_service.session_recordings = {}

    def test_complete_collaboration_workflow(self, client, test_user):
        """
        Test complete collaboration workflow:
        1. Host creates session
        2. Participants join session
        3. Code changes are synchronized
        4. Session is recorded
        5. Session can be replayed
        6. Verify end-to-end data flow
        """
        # Step 1: Host creates session
        host_id = str(test_user['_id'])
        create_data = {
            "user_id": host_id,
            "username": test_user['name'],
            "assignment_id": "test_assignment_123",
            "title": "Test Session",
            "is_public": True
        }

        response = client.post('/api/collaboration/create-session', json=create_data)
        assert response.status_code == 200
        session_data = response.json['data']
        session_id = session_data['session_id']

        assert session_id is not None
        assert session_data['title'] == "Test Session"
        assert session_data['host_id'] == host_id
        assert session_data['status'] == "waiting"

        # Verify session in service
        assert session_id in collaboration_service.active_sessions
        assert collaboration_service.user_sessions[host_id] == session_id

        # Step 2: Participant joins session
        participant_id = "participant_456"
        join_data = {
            "session_id": session_id,
            "user_id": participant_id,
            "username": "Participant User",
            "role": "participant"
        }

        response = client.post('/api/collaboration/join-session', json=join_data)
        assert response.status_code == 200
        join_result = response.json['data']

        assert join_result['session_id'] == session_id
        # Check participants count (Host + Participant = 2)
        assert len(join_result['participants']) == 2

        # Verify participant in service
        assert collaboration_service.user_sessions[participant_id] == session_id
        session = collaboration_service.active_sessions[session_id]
        assert participant_id in session.participants
        assert session.status.value == "active"  # Should be active with >1 user

        # Step 3: Code changes are synchronized
        # We simulate this by calling the service method directly as WebSocket testing is complex
        change_data = {
            "operation": "insert",
            "position": 0,
            "content": "print('Hello World')",
            "length": 0
        }

        # Mock WebSocket emit to verify broadcast
        with patch('services.collaboration_service.CollaborationService._broadcast_to_session') as mock_broadcast:
            success = collaboration_service.apply_code_change(host_id, change_data)
            assert success is True

            # Verify code content updated
            assert session.code_content == "print('Hello World')# Start coding here...\n"

            # Verify broadcast called
            mock_broadcast.assert_called()
            call_args = mock_broadcast.call_args
            assert call_args[0][0] == session_id
            assert call_args[0][1]['type'] == 'code_change'

        # Step 4: Session is recorded (automatic in this implementation)
        # Verify change history
        assert len(session.change_history) == 1
        assert session.change_history[0].content == "print('Hello World')"

        # Step 5: Session can be replayed
        response = client.get(f'/api/collaboration/session/{session_id}/recording')
        assert response.status_code == 200
        recording_data = response.json['data']

        assert recording_data['session_id'] == session_id
        assert len(recording_data['events']) >= 1
        assert recording_data['events'][0]['type'] == 'code_change'
        assert recording_data['events'][0]['change']['content'] == "print('Hello World')"

        # Step 6: Verify end-to-end data flow - Request Help
        help_data = {
            "session_id": session_id,
            "user_id": participant_id,
            "message": "Need help with syntax"
        }

        response = client.post('/api/collaboration/request-help', json=help_data)
        assert response.status_code == 200
        assert response.json['status'] == 'success'

        # Verify session state updated
        assert session.lecturer_assistance is True

        # Step 7: Leave session
        leave_data = {"user_id": participant_id}
        response = client.post('/api/collaboration/leave-session', json=leave_data)
        assert response.status_code == 200

        # Verify participant removed/offline
        assert not session.participants[participant_id].is_online
        assert participant_id not in collaboration_service.user_sessions

    def test_collaboration_join_failure(self, client):
        """Test failure when joining invalid session"""
        join_data = {
            "session_id": "invalid_session_id",
            "user_id": "user_123",
            "username": "Test User"
        }

        response = client.post('/api/collaboration/join-session', json=join_data)
        assert response.status_code == 404
        assert response.json['status'] == 'error'

    def test_public_sessions_list(self, client):
        """Test retrieving public sessions"""
        # Create a public session
        collaboration_service.create_session(
            host_id="host_1",
            username="Host 1",
            assignment_id="assign_1",
            title="Public Session 1",
            is_public=True
        )

        # Create a private session
        collaboration_service.create_session(
            host_id="host_2",
            username="Host 2",
            assignment_id="assign_2",
            title="Private Session",
            is_public=False
        )

        response = client.get('/api/collaboration/public-sessions')
        assert response.status_code == 200
        data = response.json['data']

        # Should only see the public session
        # Note: Session must be active or waiting. Newly created are waiting.
        # But get_public_sessions filters by online participants < max.
        # Since we just created them, they have 1 participant (host).

        public_sessions = data['sessions']
        assert len(public_sessions) >= 1
        titles = [s['title'] for s in public_sessions]
        assert "Public Session 1" in titles
        assert "Private Session" not in titles
