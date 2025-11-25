"""
Enhanced Security Middleware
Implements enterprise-grade security features
"""
from flask import request, abort, g
from functools import wraps
import hashlib
import hmac
import time
from typing import Optional
from config.security_config import (
    CSP_POLICY, SECURITY_HEADERS, API_KEY_HEADER,
    RATE_LIMIT_RULES
)

class SecurityMiddleware:
    """Enhanced security middleware with enterprise features"""

    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initialize security middleware"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)

        # Initialize rate limiter
        from flask_limiter import Limiter
        from flask_limiter.util import get_remote_address

        self.limiter = Limiter(
            app=app,
            key_func=get_remote_address,
            default_limits=["200 per day", "50 per hour"],
            storage_uri="redis://localhost:6379"
        )

    def before_request(self):
        """Execute before each request"""
        # Validate API key for  external requests
        if request.path.startswith('/api/external'):
            self._validate_api_key()

        # Validate request signature for critical operations
        if request.method in ['POST', 'PUT', 'DELETE']:
            if request.path.startswith('/api/critical'):
                self._validate_request_signature()

        # Track request for audit
        g.request_start_time = time.time()

    def after_request(self, response):
        """Add security headers to response"""
        # Add CSP header
        csp_string = '; '.join([
            f"{key} {' '.join(values)}"
            for key, values in CSP_POLICY.items()
        ])
        response.headers['Content-Security-Policy'] = csp_string

        # Add other security headers
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value

        # Add request timing for monitoring
        if hasattr(g, 'request_start_time'):
            duration = time.time() - g.request_start_time
            response.headers['X-Response-Time'] = f"{duration:.3f}s"

        return response

    def _validate_api_key(self):
        """Validate API key from header"""
        api_key = request.headers.get(API_KEY_HEADER)

        if not api_key:
            abort(401, description="API key required")

        # Validate against stored keys (implement your validation logic)
        if not self._is_valid_api_key(api_key):
            abort(403, description="Invalid API key")

    def _is_valid_api_key(self, api_key: str) -> bool:
        """Check if API key is valid"""
        # TODO: Implement actual validation against database/cache
        # This is a placeholder
        from flask import current_app
        valid_keys = current_app.config.get('VALID_API_KEYS', [])
        return api_key in valid_keys

    def _validate_request_signature(self):
        """Validate HMAC signature for critical requests"""
        signature = request.headers.get('X-Signature')
        timestamp = request.headers.get('X-Timestamp')

        if not signature or not timestamp:
            abort(401, description="Request signature required")

        # Check timestamp (prevent replay attacks)
        try:
            req_time = float(timestamp)
            if abs(time.time() - req_time) > 300:  # 5 minute window
                abort(401, description="Request timestamp expired")
        except ValueError:
            abort(401, description="Invalid timestamp")

        # Validate signature
        payload = request.get_data()
        expected_sig = self._generate_signature(payload, timestamp)

        if not hmac.compare_digest(signature, expected_sig):
            abort(403, description="Invalid request signature")

    def _generate_signature(self, payload: bytes, timestamp: str) -> str:
        """Generate HMAC signature for request"""
        from flask import current_app
        secret = current_app.config.get('API_SECRET_KEY', '').encode()

        message = timestamp.encode() + payload
        signature = hmac.new(secret, message, hashlib.sha256).hexdigest()
        return signature


def require_api_key(f):
    """Decorator to require API key for endpoint"""
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get(API_KEY_HEADER)
        if not api_key:
            abort(401, description="API key required")
        # Validate API key here
        return f(*args, **kwargs)
    return decorated


def require_signature(f):
    """Decorator to require request signature"""
    @wraps(f)
    def decorated(*args, **kwargs):
        signature = request.headers.get('X-Signature')
        if not signature:
            abort(401, description="Request signature required")
        # Validate signature here
        return f(*args, **kwargs)
    return decorated


# Initialize middleware
security_middleware = SecurityMiddleware()
