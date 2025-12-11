"""
Rate Limiting Configuration
Defines rate limits for different user roles and endpoints
"""

# Default rate limits (requests per time window)
DEFAULT_LIMITS = {
    'student': {
        'per_minute': 30,
        'per_hour': 200,
        'per_day': 1000
    },
    'lecturer': {
        'per_minute': 60,
        'per_hour': 500,
        'per_day': 5000
    },
    'admin': {
        'per_minute': 120,
        'per_hour': 1000,
        'per_day': 10000
    },
    'anonymous': {
        'per_minute': 10,
        'per_hour': 50,
        'per_day': 200
    }
}

# Endpoint-specific rate limits
ENDPOINT_LIMITS = {
    # Authentication endpoints - stricter limits to prevent brute force
    '/api/auth/login': {
        'limit': '5 per minute',
        'key_func': lambda: request.remote_addr  # IP-based
    },
    '/api/auth/signup': {
        'limit': '3 per hour',
        'key_func': lambda: request.remote_addr
    },
    '/api/auth/reset-password': {
        'limit': '3 per hour',
        'key_func': lambda: request.remote_addr
    },

    # Code submission - moderate limits
    '/api/submissions/submit': {
        'student': '20 per hour',
        'lecturer': '100 per hour'
    },

    # Plagiarism checking - resource intensive
    '/api/plagiarism/check': {
        'student': '10 per hour',
        'lecturer': '50 per hour'
    },

    # Code execution - very resource intensive
    '/api/code/execute': {
        'student': '30 per hour',
        'lecturer': '100 per hour'
    },

    # AI grading - expensive API calls
    '/api/grading/grade': {
        'student': '20 per hour',
        'lecturer': '100 per hour'
    },

    # Dashboard/analytics - lenient
    '/api/dashboard': {
        'student': '100 per hour',
        'lecturer': '200 per hour'
    },

    # Leaderboard - very lenient
    '/api/gamification/leaderboard': {
        'student': '60 per minute',
        'lecturer': '120 per minute'
    }
}

# Rate limit exceeded messages
RATE_LIMIT_MESSAGE = {
    'default': 'Rate limit exceeded. Please try again later.',
    'auth': 'Too many authentication attempts. Please try again in {retry_after} seconds.',
    'submission': 'Too many submissions. Please wait {retry_after} seconds before submitting again.',
    'execution': 'Code execution rate limit reached. Please wait {retry_after} seconds.',
}

# Redis configuration for distributed rate limiting
RATE_LIMIT_STORAGE_URL = 'redis://localhost:6379/1'  # Use DB 1 for rate limits

# Strategy for rate limit key generation
def get_user_rate_limit_key():
    """Generate rate limit key based on user ID or IP"""
    from flask import session, request

    # If authenticated, use user ID
    if 'user_id' in session:
        return f"user:{session['user_id']}"

    # Otherwise use IP address
    return f"ip:{request.remote_addr}"

def get_user_role():
    """Get current user's role for role-based limits"""
    from flask import session

    if 'role' in session:
        return session['role']

    return 'anonymous'

# Enable/disable rate limiting
RATE_LIMITING_ENABLED = True

# Exempted IPs (for testing, monitoring, etc.)
RATE_LIMIT_EXEMPT_IPS = [
    '127.0.0.1',
    'localhost'
]

# Headers to include in rate limit responses
RATE_LIMIT_HEADERS_ENABLED = True
