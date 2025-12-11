"""
Security Audit Logging Service
Tracks and logs all security-relevant events
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


class SecurityEventType(Enum):
    """Types of security events"""
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    LOGOUT = "logout"
    PASSWORD_CHANGE = "password_change"
    PASSWORD_RESET_REQUEST = "password_reset_request"
    PASSWORD_RESET_COMPLETE = "password_reset_complete"
    MFA_ENABLED = "mfa_enabled"
    MFA_DISABLED = "mfa_disabled"
    MFA_VERIFICATION_SUCCESS = "mfa_verification_success"
    MFA_VERIFICATION_FAILURE = "mfa_verification_failure"
    PERMISSION_CHANGE = "permission_change"
    ROLE_CHANGE = "role_change"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    DATA_DELETION = "data_deletion"
    ACCOUNT_LOCKED = "account_locked"
    ACCOUNT_UNLOCKED = "account_unlocked"


class SecurityAuditService:
    """Service for security audit logging and monitoring"""

    def __init__(self, db):
        self.db = db
        self.audit_log = db['security_audit_log']
        self.failed_attempts = db['failed_login_attempts']

        # Create indexes for efficient querying
        self.audit_log.create_index([('timestamp', -1)])
        self.audit_log.create_index([('user_id', 1), ('timestamp', -1)])
        self.audit_log.create_index([('event_type', 1), ('timestamp', -1)])
        self.audit_log.create_index([('ip_address', 1), ('timestamp', -1)])
        self.failed_attempts.create_index([('ip_address', 1), ('timestamp', -1)])

    def log_event(
        self,
        event_type: SecurityEventType,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict] = None,
        severity: str = "info"
    ) -> str:
        """
        Log a security event

        Args:
            event_type: Type of security event
            user_id: User identifier (if applicable)
            ip_address: IP address of the request
            user_agent: User agent string
            details: Additional event details
            severity: Event severity (info, warning, critical)

        Returns:
            Event ID
        """
        event = {
            'event_type': event_type.value,
            'user_id': user_id,
            'ip_address': ip_address,
            'user_agent': user_agent,
            'details': details or {},
            'severity': severity,
            'timestamp': datetime.utcnow()
        }

        result = self.audit_log.insert_one(event)

        # Check for suspicious patterns
        self._check_suspicious_activity(event)

        return str(result.inserted_id)

    def log_login_attempt(
        self,
        email: str,
        success: bool,
        ip_address: str,
        user_agent: str,
        user_id: Optional[str] = None,
        failure_reason: Optional[str] = None
    ):
        """
        Log a login attempt

        Args:
            email: User email
            success: Whether login was successful
            ip_address: IP address
            user_agent: User agent
            user_id: User ID (if successful)
            failure_reason: Reason for failure (if applicable)
        """
        if success:
            self.log_event(
                SecurityEventType.LOGIN_SUCCESS,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details={'email': email},
                severity="info"
            )
            # Clear failed attempts on successful login
            self.failed_attempts.delete_many({
                'email': email,
                'ip_address': ip_address
            })
        else:
            self.log_event(
                SecurityEventType.LOGIN_FAILURE,
                ip_address=ip_address,
                user_agent=user_agent,
                details={'email': email, 'reason': failure_reason},
                severity="warning"
            )
            # Track failed attempt
            self._track_failed_attempt(email, ip_address)

    def _track_failed_attempt(self, email: str, ip_address: str):
        """Track failed login attempts"""
        self.failed_attempts.insert_one({
            'email': email,
            'ip_address': ip_address,
            'timestamp': datetime.utcnow()
        })

        # Check if account should be locked
        recent_failures = self.get_failed_attempts(email, minutes=30)
        if len(recent_failures) >= 5:
            self.log_event(
                SecurityEventType.ACCOUNT_LOCKED,
                details={'email': email, 'reason': 'Too many failed attempts'},
                severity="critical"
            )

    def get_failed_attempts(
        self,
        email: str,
        minutes: int = 30
    ) -> List[Dict]:
        """
        Get recent failed login attempts

        Args:
            email: User email
            minutes: Time window in minutes

        Returns:
            List of failed attempts
        """
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        return list(self.failed_attempts.find({
            'email': email,
            'timestamp': {'$gte': cutoff}
        }))

    def get_user_activity(
        self,
        user_id: str,
        limit: int = 100,
        event_types: Optional[List[SecurityEventType]] = None
    ) -> List[Dict]:
        """
        Get security events for a user

        Args:
            user_id: User identifier
            limit: Maximum number of events to return
            event_types: Filter by event types

        Returns:
            List of security events
        """
        query = {'user_id': user_id}

        if event_types:
            query['event_type'] = {'$in': [et.value for et in event_types]}

        return list(self.audit_log.find(query)
                   .sort('timestamp', -1)
                   .limit(limit))

    def get_suspicious_activity(
        self,
        hours: int = 24,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get suspicious security events

        Args:
            hours: Time window in hours
            limit: Maximum number of events

        Returns:
            List of suspicious events
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        return list(self.audit_log.find({
            'severity': {'$in': ['warning', 'critical']},
            'timestamp': {'$gte': cutoff}
        }).sort('timestamp', -1).limit(limit))

    def _check_suspicious_activity(self, event: Dict):
        """Check for suspicious activity patterns"""
        # Check for multiple failed logins from same IP
        if event['event_type'] == SecurityEventType.LOGIN_FAILURE.value:
            recent_failures = list(self.audit_log.find({
                'event_type': SecurityEventType.LOGIN_FAILURE.value,
                'ip_address': event['ip_address'],
                'timestamp': {'$gte': datetime.utcnow() - timedelta(minutes=10)}
            }))

            if len(recent_failures) >= 10:
                self.log_event(
                    SecurityEventType.SUSPICIOUS_ACTIVITY,
                    ip_address=event['ip_address'],
                    details={
                        'reason': 'Multiple failed logins from same IP',
                        'count': len(recent_failures)
                    },
                    severity="critical"
                )

    def get_security_metrics(self, hours: int = 24) -> Dict:
        """
        Get security metrics for dashboard

        Args:
            hours: Time window in hours

        Returns:
            Dictionary of security metrics
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)

        # Count events by type
        pipeline = [
            {'$match': {'timestamp': {'$gte': cutoff}}},
            {'$group': {
                '_id': '$event_type',
                'count': {'$sum': 1}
            }}
        ]

        event_counts = {
            item['_id']: item['count']
            for item in self.audit_log.aggregate(pipeline)
        }

        # Get failed login count
        failed_logins = event_counts.get(SecurityEventType.LOGIN_FAILURE.value, 0)

        # Get rate limit violations
        rate_limit_violations = event_counts.get(SecurityEventType.RATE_LIMIT_EXCEEDED.value, 0)

        # Get suspicious activity count
        suspicious_count = self.audit_log.count_documents({
            'severity': 'critical',
            'timestamp': {'$gte': cutoff}
        })

        return {
            'time_window_hours': hours,
            'total_events': sum(event_counts.values()),
            'failed_logins': failed_logins,
            'rate_limit_violations': rate_limit_violations,
            'suspicious_activity_count': suspicious_count,
            'event_breakdown': event_counts,
            'generated_at': datetime.utcnow()
        }

    def export_audit_log(
        self,
        start_date: datetime,
        end_date: datetime,
        format: str = 'json'
    ) -> List[Dict]:
        """
        Export audit log for compliance

        Args:
            start_date: Start date
            end_date: End date
            format: Export format (json, csv)

        Returns:
            List of audit events
        """
        events = list(self.audit_log.find({
            'timestamp': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('timestamp', 1))

        return events
