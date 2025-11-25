# Security Configuration
# Implements OWASP Top 10 protections and enterprise security

# Content Security Policy (CSP) - Strict Mode
CSP_POLICY = {
    'default-src': ["'self'"],
    'script-src': ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
    'style-src': ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
    'font-src': ["'self'", "https://fonts.gstatic.com"],
    'img-src': ["'self'", "data:", "https:"],
    'connect-src': ["'self'"],
    'frame-ancestors': ["'none'"],
    'base-uri': ["'self'"],
    'form-action': ["'self'"]
}

# Security Headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}

# API Rate Limiting (per hour)
RATE_LIMIT_RULES = {
    'default': '100/hour',
    'login': '10/hour',
    'submission': '50/hour',
    'plagiarism': '20/hour',
    'api_calls': '200/hour'
}

# API Key Configuration
API_KEY_HEADER = 'X-API-Key'
API_KEY_LENGTH = 32  # bytes

# Session Security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour

# Password Policy
PASSWORD_MIN_LENGTH = 12
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGITS = True
PASSWORD_REQUIRE_SPECIAL = True

# Encryption
ENCRYPTION_ALGORITHM = 'AES-256-GCM'
KEY_DERIVATION_ITERATIONS = 100000

# OAuth2/SAML
OAUTH_PROVIDERS = {
    'google': {
        'client_id': '${GOOGLE_CLIENT_ID}',
        'client_secret': '${GOOGLE_CLIENT_SECRET}',
        'redirect_uri': '/auth/google/callback'
    },
    'microsoft': {
        'client_id': '${MICROSOFT_CLIENT_ID}',
        'client_secret': '${MICROSOFT_CLIENT_SECRET}',
        'redirect_uri': '/auth/microsoft/callback'
    }
}

# Audit Logging
AUDIT_EVENTS = [
    'user_login',
    'user_logout',
    'code_submission',
    'assignment_creation',
    'grade_modification',
    'plagiarism_detection',
    'admin_action'
]
