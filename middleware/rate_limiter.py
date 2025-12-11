"""
Rate Limiting Middleware
Implements Flask-Limiter with Redis backend for distributed rate limiting
"""

import logging
from functools import wraps

from flask import jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config.rate_limit_config import (
    DEFAULT_LIMITS,
    ENDPOINT_LIMITS,
    RATE_LIMIT_EXEMPT_IPS,
    RATE_LIMIT_HEADERS_ENABLED,
    RATE_LIMIT_MESSAGE,
    RATE_LIMIT_STORAGE_URL,
    RATE_LIMITING_ENABLED,
    get_user_rate_limit_key,
    get_user_role,
)

logger = logging.getLogger(__name__)

# Initialize limiter (will be configured in init_rate_limiter)
limiter = None


def init_rate_limiter(app):
    """Initialize Flask-Limiter with the Flask app"""
    global limiter

    try:
        limiter = Limiter(
            app=app,
            key_func=get_user_rate_limit_key,
            storage_uri=RATE_LIMIT_STORAGE_URL,
            storage_options={},
            default_limits=[],  # We'll set limits per endpoint
            headers_enabled=RATE_LIMIT_HEADERS_ENABLED,
            swallow_errors=True,  # Don't crash if Redis is down
            enabled=RATE_LIMITING_ENABLED,
        )

        # Register error handler
        @app.errorhandler(429)
        def ratelimit_handler(e):
            """Custom handler for rate limit exceeded"""
            logger.warning("Rate limit exceeded: {request.remote_addr} - {request.endpoint}")

            return (
                jsonify(
                    {
                        "error": "rate_limit_exceeded",
                        "message": RATE_LIMIT_MESSAGE["default"],
                        "retry_after": e.description,
                    }
                ),
                429,
            )

        logger.info("Rate limiter initialized successfully")
        return limiter

    except (ValueError, KeyError, AttributeError) as e:
        logger.error("Failed to initialize rate limiter: {str(e)}")
        # Return a no-op limiter if Redis is not available
        return None


def role_based_limit(limits_dict):
    """
    Decorator to apply role-based rate limits

    Usage:
        @role_based_limit({'student': '20 per hour', 'lecturer': '100 per hour'})
    """

    def decorator(func):
        """decorator function.

        Returns:
            Response data
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper function.

            Returns:
                Response data
            """

            if not RATE_LIMITING_ENABLED or limiter is None:
                return func(*args, **kwargs)

            # Get user's role
            role = get_user_role()

            # Get limit for this role
            limit = limits_dict.get(role, limits_dict.get("student", "10 per hour"))

            # Apply limit dynamically
            limited_func = limiter.limit(limit)(func)
            return limited_func(*args, **kwargs)

        return wrapper

    return decorator


def exempt_when_internal():
    """Decorator to exempt internal/admin requests from rate limiting"""

    def decorator(func):
        """decorator function.

        Returns:
            Response data
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """wrapper function.

            Returns:
                Response data
            """

            # Check if request is from exempt IP
            if request.remote_addr in RATE_LIMIT_EXEMPT_IPS:
                return func(*args, **kwargs)

            # Check if user is admin
            if session.get("role") == "admin":
                return func(*args, **kwargs)

            return func(*args, **kwargs)

        return wrapper

    return decorator


def dynamic_rate_limit():
    """
    Dynamically determine rate limit based on user role
    Returns limit string like "50 per hour"
    """
    role = get_user_role()
    limits = DEFAULT_LIMITS.get(role, DEFAULT_LIMITS["anonymous"])

    # Return the most restrictive limit (per hour)
    return f"{limits['per_hour']} per hour"


def check_rate_limit_manually(key, limit):
    """
    Manually check rate limit for a specific key
    Useful for custom rate limiting logic

    Returns:
        (bool, int): (is_allowed, retry_after_seconds)
    """
    if not RATE_LIMITING_ENABLED or limiter is None:
        return True, 0

    try:
        # Get current limit
        current = limiter.storage.get(key)

        if current is None:
            return True, 0

        # Parse limit (e.g., "50 per hour")
        parts = limit.split()
        max_requests = int(parts[0])

        if current >= max_requests:
            # Calculate retry after (simplified)
            retry_after = 60  # Default 1 minute
            return False, retry_after

        return True, 0

    except (ValueError, KeyError, AttributeError) as e:
        logger.error("Rate limit check failed: {str(e)}")
        # Allow request if check fails
        return True, 0


def increment_custom_counter(key, limit, expire=3600):
    """
    Increment a custom rate limit counter
    Useful for tracking specific actions

    Args:
        key: Redis key for the counter
        limit: Maximum allowed value
        expire: Expiration time in seconds

    Returns:
        (bool, int, int): (is_allowed, current_count, limit)
    """
    if not RATE_LIMITING_ENABLED or limiter is None:
        return True, 0, limit

    try:
        # Increment counter
        current = limiter.storage.incr(key, expire=expire)

        # Check if limit exceeded
        is_allowed = current <= limit

        return is_allowed, current, limit

    except (ValueError, KeyError, AttributeError) as e:
        logger.error("Counter increment failed: {str(e)}")
        return True, 0, limit


# Pre-configured decorators for common scenarios
def auth_rate_limit():
    """Strict rate limit for authentication endpoints"""
    return limiter.limit("5 per minute", get_user_rate_limit_key)


def submission_rate_limit():
    """Moderate rate limit for code submissions."""

    def get_limit():
        """get_limit function.

        Returns:
            Response data
        """

        role = get_user_role()
        if role == "lecturer":
            return "100 per hour"
        return "20 per hour"

    return limiter.limit(get_limit, key_func=get_user_rate_limit_key)


def execution_rate_limit():
    """Rate limit for code execution"""

    def get_limit():
        """get_limit function.

        Returns:
            Response data
        """

        role = get_user_role()
        if role == "lecturer":
            return "100 per hour"
        return "30 per hour"

    return limiter.limit(get_limit, key_func=get_user_rate_limit_key)


def plagiarism_rate_limit():
    """Rate limit for plagiarism checking"""

    def get_limit():
        """get_limit function.

        Returns:
            Response data
        """

        role = get_user_role()
        if role == "lecturer":
            return "50 per hour"
        return "10 per hour"

    return limiter.limit(get_limit, key_func=get_user_rate_limit_key)


def dashboard_rate_limit():
    """Lenient rate limit for dashboard/analytics"""

    def get_limit():
        """get_limit function.

        Returns:
            Response data
        """

        role = get_user_role()
        if role == "lecturer":
            return "200 per hour"
        return "100 per hour"

    return limiter.limit(get_limit, key_func=get_user_rate_limit_key)


# Utility functions
def get_rate_limit_status(key=None):
    """
    Get current rate limit status for a key

    Returns:
        dict: {'limit': int, 'remaining': int, 'reset': timestamp}
    """
    if not RATE_LIMITING_ENABLED or limiter is None:
        return {"limit": 999999, "remaining": 999999, "reset": 0}

    if key is None:
        key = get_user_rate_limit_key()

    try:
        # This would need to be implemented based on Flask-Limiter's storage
        # For now, return a placeholder
        return {"limit": 100, "remaining": 95, "reset": 3600}
    except (ValueError, KeyError, AttributeError) as e:
        logger.error("Failed to get rate limit status: {str(e)}")
        return {"limit": 0, "remaining": 0, "reset": 0}


def reset_rate_limit(key):
    """Reset rate limit for a specific key (admin function)"""
    if not RATE_LIMITING_ENABLED or limiter is None:
        return True

    try:
        limiter.storage.reset(key)
        logger.info("Rate limit reset for key: {key}")
        return True
    except (ValueError, KeyError, AttributeError) as e:
        logger.error("Failed to reset rate limit: {str(e)}")
        return False
