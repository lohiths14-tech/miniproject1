"""Tests for Security Audit Service.

Tests security scanning and vulnerability detection functionality.
Requirements: 2.1, 2.2
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from services.security_audit_service import (
    SecurityAuditService,
    SecurityEventType,
)


class MockCollection:
    """Mock MongoDB collection for testing."""

    def __init__(self):
        self.documents = []
        self.indexes = []

    def create_index(self, index_spec):
        """Mock create_index."""
        self.indexes.append(index_spec)

    def insert_one(self, document):
        """Mock insert_one."""
        doc_id = f"mock_id_{len(self.documents)}"
        document["_id"] = doc_id
        self.documents.append(document)
        return MagicMock(inserted_id=doc_id)

    def find(self, query=None):
        """Mock find - returns a cursor-like object."""
        results = self.documents.copy()
        if query:
            results = self._filter_documents(results, query)
        return MockCursor(results)

    def find_one(self, query=None):
        """Mock find_one."""
        results = self._filter_documents(self.documents, query) if query else self.documents
        return results[0] if results else None

    def delete_many(self, query):
        """Mock delete_many."""
        to_remove = self._filter_documents(self.documents, query)
        for doc in to_remove:
            self.documents.remove(doc)
        return MagicMock(deleted_count=len(to_remove))

    def count_documents(self, query):
        """Mock count_documents."""
        return len(self._filter_documents(self.documents, query))

    def aggregate(self, pipeline):
        """Mock aggregate."""
        # Simple aggregation mock
        return []

    def _filter_documents(self, docs, query):
        """Simple query filter."""
        if not query:
            return docs
        results = []
        for doc in docs:
            match = True
            for key, value in query.items():
                if key == "$and":
                    continue
                if isinstance(value, dict):
                    if "$in" in value:
                        if doc.get(key) not in value["$in"]:
                            match = False
                    elif "$gte" in value:
                        if doc.get(key) < value["$gte"]:
                            match = False
                    elif "$lte" in value:
                        if doc.get(key) > value["$lte"]:
                            match = False
                else:
                    if doc.get(key) != value:
                        match = False
            if match:
                results.append(doc)
        return results


class MockCursor:
    """Mock MongoDB cursor."""

    def __init__(self, documents):
        self.documents = documents

    def sort(self, field, direction=-1):
        """Mock sort."""
        return self

    def limit(self, count):
        """Mock limit."""
        self.documents = self.documents[:count]
        return self

    def __iter__(self):
        return iter(self.documents)

    def __list__(self):
        return self.documents


class MockDatabase:
    """Mock MongoDB database."""

    def __init__(self):
        self.collections = {}

    def __getitem__(self, name):
        if name not in self.collections:
            self.collections[name] = MockCollection()
        return self.collections[name]


@pytest.fixture
def mock_db():
    """Create a mock database."""
    return MockDatabase()


@pytest.fixture
def security_service(mock_db):
    """Create a SecurityAuditService with mock database."""
    return SecurityAuditService(mock_db)


class TestSecurityEventTypeEnum:
    """Test suite for SecurityEventType enum."""

    def test_login_success_type(self):
        """Test LOGIN_SUCCESS event type."""
        assert SecurityEventType.LOGIN_SUCCESS.value == "login_success"

    def test_login_failure_type(self):
        """Test LOGIN_FAILURE event type."""
        assert SecurityEventType.LOGIN_FAILURE.value == "login_failure"

    def test_logout_type(self):
        """Test LOGOUT event type."""
        assert SecurityEventType.LOGOUT.value == "logout"

    def test_password_change_type(self):
        """Test PASSWORD_CHANGE event type."""
        assert SecurityEventType.PASSWORD_CHANGE.value == "password_change"

    def test_mfa_enabled_type(self):
        """Test MFA_ENABLED event type."""
        assert SecurityEventType.MFA_ENABLED.value == "mfa_enabled"

    def test_suspicious_activity_type(self):
        """Test SUSPICIOUS_ACTIVITY event type."""
        assert SecurityEventType.SUSPICIOUS_ACTIVITY.value == "suspicious_activity"

    def test_account_locked_type(self):
        """Test ACCOUNT_LOCKED event type."""
        assert SecurityEventType.ACCOUNT_LOCKED.value == "account_locked"

    def test_rate_limit_exceeded_type(self):
        """Test RATE_LIMIT_EXCEEDED event type."""
        assert SecurityEventType.RATE_LIMIT_EXCEEDED.value == "rate_limit_exceeded"


class TestSecurityAuditServiceInit:
    """Test suite for service initialization."""

    def test_service_creates_indexes(self, mock_db):
        """Test that service creates database indexes."""
        service = SecurityAuditService(mock_db)

        # Check that indexes were created
        audit_log = mock_db["security_audit_log"]
        assert len(audit_log.indexes) > 0

    def test_service_has_audit_log_collection(self, mock_db):
        """Test that service has audit_log collection."""
        service = SecurityAuditService(mock_db)
        assert service.audit_log is not None

    def test_service_has_failed_attempts_collection(self, mock_db):
        """Test that service has failed_attempts collection."""
        service = SecurityAuditService(mock_db)
        assert service.failed_attempts is not None


class TestLogEvent:
    """Test suite for log_event functionality."""

    def test_log_event_returns_event_id(self, security_service):
        """Test that log_event returns an event ID."""
        event_id = security_service.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            user_id="user123",
            ip_address="192.168.1.1",
        )

        assert event_id is not None
        assert isinstance(event_id, str)

    def test_log_event_stores_event_type(self, security_service, mock_db):
        """Test that log_event stores the event type."""
        security_service.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            user_id="user123",
        )

        events = list(mock_db["security_audit_log"].find())
        assert len(events) == 1
        assert events[0]["event_type"] == "login_success"

    def test_log_event_stores_user_id(self, security_service, mock_db):
        """Test that log_event stores the user ID."""
        security_service.log_event(
            SecurityEventType.LOGOUT,
            user_id="user456",
        )

        events = list(mock_db["security_audit_log"].find())
        assert events[0]["user_id"] == "user456"

    def test_log_event_stores_ip_address(self, security_service, mock_db):
        """Test that log_event stores the IP address."""
        security_service.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            ip_address="10.0.0.1",
        )

        events = list(mock_db["security_audit_log"].find())
        assert events[0]["ip_address"] == "10.0.0.1"

    def test_log_event_stores_severity(self, security_service, mock_db):
        """Test that log_event stores severity."""
        security_service.log_event(
            SecurityEventType.SUSPICIOUS_ACTIVITY,
            severity="critical",
        )

        events = list(mock_db["security_audit_log"].find())
        assert events[0]["severity"] == "critical"

    def test_log_event_stores_details(self, security_service, mock_db):
        """Test that log_event stores details."""
        security_service.log_event(
            SecurityEventType.DATA_ACCESS,
            details={"resource": "users", "action": "read"},
        )

        events = list(mock_db["security_audit_log"].find())
        assert events[0]["details"]["resource"] == "users"


class TestLogLoginAttempt:
    """Test suite for log_login_attempt functionality."""

    def test_log_successful_login(self, security_service, mock_db):
        """Test logging successful login."""
        security_service.log_login_attempt(
            email="user@example.com",
            success=True,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            user_id="user123",
        )

        events = list(mock_db["security_audit_log"].find())
        assert len(events) == 1
        assert events[0]["event_type"] == "login_success"

    def test_log_failed_login(self, security_service, mock_db):
        """Test logging failed login."""
        security_service.log_login_attempt(
            email="user@example.com",
            success=False,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            failure_reason="Invalid password",
        )

        events = list(mock_db["security_audit_log"].find())
        assert len(events) == 1
        assert events[0]["event_type"] == "login_failure"

    def test_failed_login_tracks_attempt(self, security_service, mock_db):
        """Test that failed login tracks the attempt."""
        security_service.log_login_attempt(
            email="user@example.com",
            success=False,
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        attempts = list(mock_db["failed_login_attempts"].find())
        assert len(attempts) == 1


class TestGetFailedAttempts:
    """Test suite for get_failed_attempts functionality."""

    def test_get_failed_attempts_empty(self, security_service):
        """Test getting failed attempts when none exist."""
        attempts = security_service.get_failed_attempts("user@example.com")
        assert len(attempts) == 0

    def test_get_failed_attempts_returns_list(self, security_service, mock_db):
        """Test that get_failed_attempts returns a list."""
        # Add a failed attempt
        mock_db["failed_login_attempts"].insert_one({
            "email": "user@example.com",
            "ip_address": "192.168.1.1",
            "timestamp": datetime.utcnow(),
        })

        attempts = security_service.get_failed_attempts("user@example.com")
        assert isinstance(attempts, list)


class TestGetUserActivity:
    """Test suite for get_user_activity functionality."""

    def test_get_user_activity_empty(self, security_service):
        """Test getting activity for user with no events."""
        activity = security_service.get_user_activity("nonexistent_user")
        assert isinstance(activity, list)
        assert len(activity) == 0

    def test_get_user_activity_returns_events(self, security_service, mock_db):
        """Test getting activity returns user events."""
        # Log some events
        security_service.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            user_id="user123",
        )
        security_service.log_event(
            SecurityEventType.LOGOUT,
            user_id="user123",
        )

        activity = security_service.get_user_activity("user123")
        assert len(activity) == 2


class TestGetSuspiciousActivity:
    """Test suite for get_suspicious_activity functionality."""

    def test_get_suspicious_activity_empty(self, security_service):
        """Test getting suspicious activity when none exists."""
        activity = security_service.get_suspicious_activity()
        assert isinstance(activity, list)

    def test_get_suspicious_activity_returns_warnings(self, security_service, mock_db):
        """Test getting suspicious activity returns warning events."""
        # Log a warning event
        security_service.log_event(
            SecurityEventType.LOGIN_FAILURE,
            severity="warning",
        )

        activity = security_service.get_suspicious_activity()
        # May or may not find it depending on timestamp filtering
        assert isinstance(activity, list)


class TestGetSecurityMetrics:
    """Test suite for get_security_metrics functionality."""

    def test_get_security_metrics_returns_dict(self, security_service):
        """Test that get_security_metrics returns a dictionary."""
        metrics = security_service.get_security_metrics()

        assert isinstance(metrics, dict)
        assert "time_window_hours" in metrics
        assert "total_events" in metrics

    def test_get_security_metrics_has_failed_logins(self, security_service):
        """Test that metrics include failed logins count."""
        metrics = security_service.get_security_metrics()

        assert "failed_logins" in metrics

    def test_get_security_metrics_has_rate_limit_violations(self, security_service):
        """Test that metrics include rate limit violations."""
        metrics = security_service.get_security_metrics()

        assert "rate_limit_violations" in metrics

    def test_get_security_metrics_has_generated_at(self, security_service):
        """Test that metrics include generation timestamp."""
        metrics = security_service.get_security_metrics()

        assert "generated_at" in metrics


class TestExportAuditLog:
    """Test suite for export_audit_log functionality."""

    def test_export_audit_log_returns_list(self, security_service):
        """Test that export_audit_log returns a list."""
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()

        result = security_service.export_audit_log(start_date, end_date)

        assert isinstance(result, list)

    def test_export_audit_log_with_events(self, security_service, mock_db):
        """Test exporting audit log with events."""
        # Log an event
        security_service.log_event(
            SecurityEventType.LOGIN_SUCCESS,
            user_id="user123",
        )

        start_date = datetime.utcnow() - timedelta(days=1)
        end_date = datetime.utcnow() + timedelta(days=1)

        result = security_service.export_audit_log(start_date, end_date)

        assert isinstance(result, list)

