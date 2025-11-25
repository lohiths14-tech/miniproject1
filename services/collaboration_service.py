"""
Real-time Collaboration Service
Handles WebSocket-based code sharing, pair programming sessions, and live collaboration features
"""

import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum

class SessionStatus(Enum):
    """Collaboration session status"""
    WAITING = "waiting"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"

class UserRole(Enum):
    """User roles in collaboration session"""
    HOST = "host"
    PARTICIPANT = "participant"
    OBSERVER = "observer"
    LECTURER = "lecturer"

@dataclass
class CollaborationUser:
    """User in a collaboration session"""
    user_id: str
    username: str
    role: UserRole
    cursor_position: int = 0
    last_activity: datetime = None
    is_online: bool = True
    avatar_color: str = "#007bff"

@dataclass
class CodeChange:
    """Represents a code change event"""
    change_id: str
    user_id: str
    timestamp: datetime
    operation: str  # 'insert', 'delete', 'replace'
    position: int
    content: str
    length: int = 0

@dataclass
class CollaborationSession:
    """Collaboration session data"""
    session_id: str
    title: str
    assignment_id: str
    host_id: str
    status: SessionStatus
    created_at: datetime
    updated_at: datetime
    participants: Dict[str, CollaborationUser]
    code_content: str
    language: str
    change_history: List[CodeChange]
    max_participants: int = 4
    is_public: bool = False
    lecturer_assistance: bool = False

class CollaborationService:
    def __init__(self):
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.user_sessions: Dict[str, str] = {}  # user_id -> session_id
        self.websocket_connections: Dict[str, object] = {}  # user_id -> websocket
        self.session_recordings: Dict[str, List[Dict]] = {}
        
    def create_session(self, host_id: str, username: str, assignment_id: str, 
                      title: str = None, is_public: bool = False, 
                      lecturer_assistance: bool = False) -> CollaborationSession:
        """Create a new collaboration session"""
        session_id = str(uuid.uuid4())
        
        if not title:
            title = f"{username}'s Coding Session"
        
        host_user = CollaborationUser(
            user_id=host_id,
            username=username,
            role=UserRole.HOST,
            last_activity=datetime.utcnow(),
            avatar_color=self._generate_avatar_color()
        )
        
        session = CollaborationSession(
            session_id=session_id,
            title=title,
            assignment_id=assignment_id,
            host_id=host_id,
            status=SessionStatus.WAITING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            participants={host_id: host_user},
            code_content="# Start coding here...\n",
            language="python",
            change_history=[],
            is_public=is_public,
            lecturer_assistance=lecturer_assistance
        )
        
        self.active_sessions[session_id] = session
        self.user_sessions[host_id] = session_id
        
        return session
    
    def join_session(self, session_id: str, user_id: str, username: str, 
                    role: UserRole = UserRole.PARTICIPANT) -> Optional[CollaborationSession]:
        """Join an existing collaboration session"""
        if session_id not in self.active_sessions:
            return None
        
        session = self.active_sessions[session_id]
        
        # Check if session is full
        if len(session.participants) >= session.max_participants and role != UserRole.LECTURER:
            return None
        
        # Check if user is already in session
        if user_id in session.participants:
            # Update user status to online
            session.participants[user_id].is_online = True
            session.participants[user_id].last_activity = datetime.utcnow()
        else:
            # Add new participant
            participant = CollaborationUser(
                user_id=user_id,
                username=username,
                role=role,
                last_activity=datetime.utcnow(),
                avatar_color=self._generate_avatar_color()
            )
            session.participants[user_id] = participant
        
        self.user_sessions[user_id] = session_id
        session.updated_at = datetime.utcnow()
        
        # Start session if it was waiting
        if session.status == SessionStatus.WAITING and len(session.participants) > 1:
            session.status = SessionStatus.ACTIVE
        
        # Broadcast user joined event
        self._broadcast_to_session(session_id, {
            'type': 'user_joined',
            'user': asdict(session.participants[user_id]),
            'participants_count': len(session.participants)
        })
        
        return session
    
    def leave_session(self, user_id: str) -> bool:
        """Remove user from their current session"""
        if user_id not in self.user_sessions:
            return False
        
        session_id = self.user_sessions[user_id]
        session = self.active_sessions.get(session_id)
        
        if not session or user_id not in session.participants:
            return False
        
        # Mark user as offline
        session.participants[user_id].is_online = False
        session.updated_at = datetime.utcnow()
        
        # Broadcast user left event
        self._broadcast_to_session(session_id, {
            'type': 'user_left',
            'user_id': user_id,
            'username': session.participants[user_id].username
        })
        
        # Clean up user session mapping
        del self.user_sessions[user_id]
        
        # End session if host leaves or no active participants
        active_participants = [p for p in session.participants.values() if p.is_online]
        if (session.participants[user_id].role == UserRole.HOST or 
            len(active_participants) == 0):
            self._end_session(session_id)
        
        return True
    
    def apply_code_change(self, user_id: str, change_data: Dict) -> bool:
        """Apply a code change and broadcast to all participants"""
        if user_id not in self.user_sessions:
            return False
        
        session_id = self.user_sessions[user_id]
        session = self.active_sessions.get(session_id)
        
        if not session or session.status != SessionStatus.ACTIVE:
            return False
        
        # Create change record
        change = CodeChange(
            change_id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.utcnow(),
            operation=change_data.get('operation', 'insert'),
            position=change_data.get('position', 0),
            content=change_data.get('content', ''),
            length=change_data.get('length', 0)
        )
        
        # Apply change to session content
        if change.operation == 'insert':
            session.code_content = (session.code_content[:change.position] + 
                                  change.content + 
                                  session.code_content[change.position:])
        elif change.operation == 'delete':
            session.code_content = (session.code_content[:change.position] + 
                                  session.code_content[change.position + change.length:])
        elif change.operation == 'replace':
            session.code_content = (session.code_content[:change.position] + 
                                  change.content + 
                                  session.code_content[change.position + change.length:])
        
        # Add to change history
        session.change_history.append(change)
        session.updated_at = datetime.utcnow()
        
        # Update user activity
        if user_id in session.participants:
            session.participants[user_id].last_activity = datetime.utcnow()
        
        # Broadcast change to all participants except sender
        self._broadcast_to_session(session_id, {
            'type': 'code_change',
            'change': asdict(change),
            'code_content': session.code_content
        }, exclude_user=user_id)
        
        # Record for session playback
        self._record_session_event(session_id, {
            'type': 'code_change',
            'timestamp': change.timestamp.isoformat(),
            'user_id': user_id,
            'change': asdict(change)
        })
        
        return True
    
    def update_cursor_position(self, user_id: str, position: int) -> bool:
        """Update user's cursor position and broadcast to others"""
        if user_id not in self.user_sessions:
            return False
        
        session_id = self.user_sessions[user_id]
        session = self.active_sessions.get(session_id)
        
        if not session or user_id not in session.participants:
            return False
        
        # Update cursor position
        session.participants[user_id].cursor_position = position
        session.participants[user_id].last_activity = datetime.utcnow()
        
        # Broadcast cursor update
        self._broadcast_to_session(session_id, {
            'type': 'cursor_update',
            'user_id': user_id,
            'username': session.participants[user_id].username,
            'position': position,
            'avatar_color': session.participants[user_id].avatar_color
        }, exclude_user=user_id)
        
        return True
    
    def request_lecturer_assistance(self, session_id: str, user_id: str, 
                                   message: str = None) -> bool:
        """Request lecturer assistance for a session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return False
        
        session.lecturer_assistance = True
        
        # Create assistance request event
        assistance_event = {
            'type': 'lecturer_assistance_requested',
            'session_id': session_id,
            'session_title': session.title,
            'requester_id': user_id,
            'requester_name': session.participants.get(user_id, {}).username if user_id in session.participants else 'Unknown',
            'message': message or 'Student needs help with coding problem',
            'timestamp': datetime.utcnow().isoformat(),
            'assignment_id': session.assignment_id
        }
        
        # Broadcast to session participants
        self._broadcast_to_session(session_id, assistance_event)
        
        # Here you would also notify available lecturers
        # This could integrate with your notification service
        
        return True
    
    def get_session_info(self, session_id: str) -> Optional[Dict]:
        """Get detailed session information"""
        session = self.active_sessions.get(session_id)
        if not session:
            return None
        
        return {
            'session_id': session.session_id,
            'title': session.title,
            'assignment_id': session.assignment_id,
            'status': session.status.value,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat(),
            'participants': [asdict(p) for p in session.participants.values()],
            'code_content': session.code_content,
            'language': session.language,
            'is_public': session.is_public,
            'lecturer_assistance': session.lecturer_assistance,
            'participants_count': len([p for p in session.participants.values() if p.is_online])
        }
    
    def get_public_sessions(self) -> List[Dict]:
        """Get list of public sessions available to join"""
        public_sessions = []
        
        for session in self.active_sessions.values():
            if (session.is_public and 
                session.status in [SessionStatus.WAITING, SessionStatus.ACTIVE] and
                len([p for p in session.participants.values() if p.is_online]) < session.max_participants):
                
                public_sessions.append({
                    'session_id': session.session_id,
                    'title': session.title,
                    'host_name': session.participants[session.host_id].username,
                    'participants_count': len([p for p in session.participants.values() if p.is_online]),
                    'max_participants': session.max_participants,
                    'language': session.language,
                    'created_at': session.created_at.isoformat(),
                    'lecturer_assistance': session.lecturer_assistance
                })
        
        return sorted(public_sessions, key=lambda x: x['created_at'], reverse=True)
    
    def get_session_recording(self, session_id: str) -> Optional[Dict]:
        """Get session recording for playback"""
        if session_id not in self.session_recordings:
            return None
        
        session = self.active_sessions.get(session_id)
        recording = self.session_recordings[session_id]
        
        return {
            'session_id': session_id,
            'title': session.title if session else 'Unknown Session',
            'events': recording,
            'total_duration': self._calculate_session_duration(recording),
            'participants': [asdict(p) for p in session.participants.values()] if session else []
        }
    
    def _broadcast_to_session(self, session_id: str, message: Dict, exclude_user: str = None):
        """Broadcast message to all participants in a session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        for user_id, participant in session.participants.items():
            if (participant.is_online and 
                user_id != exclude_user and 
                user_id in self.websocket_connections):
                
                try:
                    # In a real implementation, this would send via WebSocket
                    # For now, we'll store the message for the WebSocket handler to pick up
                    websocket = self.websocket_connections[user_id]
                    # websocket.send(json.dumps(message))
                except Exception as e:
                    print(f"Failed to send message to user {user_id}: {e}")
    
    def _end_session(self, session_id: str):
        """End a collaboration session"""
        session = self.active_sessions.get(session_id)
        if not session:
            return
        
        session.status = SessionStatus.ENDED
        session.updated_at = datetime.utcnow()
        
        # Broadcast session ended
        self._broadcast_to_session(session_id, {
            'type': 'session_ended',
            'session_id': session_id,
            'message': 'Collaboration session has ended'
        })
        
        # Clean up user session mappings
        for user_id in list(session.participants.keys()):
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
        
        # Remove from active sessions after a delay (for recording access)
        # In production, you'd move this to a database
        # del self.active_sessions[session_id]
    
    def _record_session_event(self, session_id: str, event: Dict):
        """Record session event for playback"""
        if session_id not in self.session_recordings:
            self.session_recordings[session_id] = []
        
        self.session_recordings[session_id].append(event)
    
    def _generate_avatar_color(self) -> str:
        """Generate a unique avatar color for users"""
        colors = [
            "#007bff", "#28a745", "#dc3545", "#ffc107", 
            "#17a2b8", "#6f42c1", "#e83e8c", "#fd7e14",
            "#20c997", "#6610f2", "#e74c3c", "#3498db"
        ]
        return colors[len(self.active_sessions) % len(colors)]
    
    def _calculate_session_duration(self, events: List[Dict]) -> int:
        """Calculate total session duration in seconds"""
        if not events:
            return 0
        
        first_event = min(events, key=lambda x: x['timestamp'])
        last_event = max(events, key=lambda x: x['timestamp'])
        
        first_time = datetime.fromisoformat(first_event['timestamp'])
        last_time = datetime.fromisoformat(last_event['timestamp'])
        
        return int((last_time - first_time).total_seconds())
    
    def register_websocket(self, user_id: str, websocket):
        """Register a WebSocket connection for a user"""
        self.websocket_connections[user_id] = websocket
    
    def unregister_websocket(self, user_id: str):
        """Unregister a WebSocket connection"""
        if user_id in self.websocket_connections:
            del self.websocket_connections[user_id]

# Global instance
collaboration_service = CollaborationService()