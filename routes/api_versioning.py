"""
API Versioning Blueprint - Handles versioned API endpoints
Implements explicit API versioning for backward compatibility
"""

from flask import Blueprint, jsonify, request


# API Version 1
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')


@api_v1.route('/health', methods=['GET'])
def health_v1():
    """Health check endpoint - v1"""
    return jsonify({
        'status': 'healthy',
        'version': 'v1',
        'api_version': '1.0.0',
        'message': 'AI Grading System API v1 is operational'
    })


@api_v1.route('/info', methods=['GET'])
def info_v1():
    """API information endpoint - v1"""
    return jsonify({
        'api_version': '1.0.0',
        'version': 'v1',
        'endpoints': {
            'auth': '/api/v1/auth',
            'submissions': '/api/v1/submissions',
            'assignments': '/api/v1/assignments',
            'gamification': '/api/v1/gamification',
            'plagiarism': '/api/v1/plagiarism',
            'collaboration': '/api/v1/collaboration',
        },
        'features': [
            'AI-powered grading',
            'Plagiarism detection',
            'Gamification',
            'Real-time collaboration',
            'Analytics'
        ]
    })


# API Version 2 (Future)
api_v2 = Blueprint('api_v2', __name__, url_prefix='/api/v2')


@api_v2.route('/health', methods=['GET'])
def health_v2():
    """Health check endpoint - v2"""
    return jsonify({
        'status': 'healthy',
        'version': 'v2',
        'api_version': '2.0.0',
        'message': 'AI Grading System API v2 is operational',
        'enhanced_features': True
    })


@api_v2.route('/info', methods=['GET'])
def info_v2():
    """API information endpoint - v2 (enhanced)"""
    return jsonify({
        'api_version': '2.0.0',
        'version': 'v2',
        'endpoints': {
            'auth': '/api/v2/auth',
            'submissions': '/api/v2/submissions',
            'assignments': '/api/v2/assignments',
            'gamification': '/api/v2/gamification',
            'plagiarism': '/api/v2/plagiarism',
            'collaboration': '/api/v2/collaboration',
            'analytics': '/api/v2/analytics'
        },
        'features': [
            'AI-powered grading with GPT-4',
            'Cross-language plagiarism detection',
            'Advanced gamification with achievements',
            'Real-time collaboration with video',
            'Predictive analytics',
            'Smart assignment generation'
        ],
        'breaking_changes': [
            'Authentication now requires JWT tokens',
            'Submission format updated',
            'New analytics endpoints'
        ]
    })


# Version negotiation middleware
def get_api_version(req=None):
    """Get API version from request (URL path or header).

    Version detection priority:
    1. URL path (e.g., /api/v1/*, /api/v2/*)
    2. API-Version header
    3. Accept header with version parameter
    4. Default to 'v1'

    Args:
        req: Optional request object. If None, uses Flask's request context.

    Returns:
        str: The API version ('v1' or 'v2')
    """
    if req is None:
        req = request

    # Check URL path first (highest priority)
    path = req.path if hasattr(req, 'path') else ''
    if '/api/v2/' in path:
        return 'v2'
    elif '/api/v1/' in path:
        return 'v1'

    # Check API-Version header
    version_header = req.headers.get('API-Version', '').lower().strip()
    if version_header:
        # Normalize version format (accept 'v1', 'v2', '1', '2', '1.0', '2.0')
        if version_header in ('v2', '2', '2.0', '2.0.0'):
            return 'v2'
        elif version_header in ('v1', '1', '1.0', '1.0.0'):
            return 'v1'
        # Return the header value if it's a valid version format
        if version_header.startswith('v'):
            return version_header

    # Check Accept header for version parameter
    accept_header = req.headers.get('Accept', '')
    if 'version=2' in accept_header or 'version=v2' in accept_header:
        return 'v2'
    elif 'version=1' in accept_header or 'version=v1' in accept_header:
        return 'v1'

    # Default to v1 for backward compatibility
    return 'v1'


def get_api_version_info(version):
    """Get detailed information about an API version.

    Args:
        version: The API version string ('v1' or 'v2')

    Returns:
        dict: Version information including endpoints and features
    """
    versions = {
        'v1': {
            'version': 'v1',
            'api_version': '1.0.0',
            'status': 'stable',
            'endpoints': {
                'auth': '/api/v1/auth',
                'submissions': '/api/v1/submissions',
                'assignments': '/api/v1/assignments',
                'gamification': '/api/v1/gamification',
                'plagiarism': '/api/v1/plagiarism',
                'collaboration': '/api/v1/collaboration',
            },
            'features': [
                'AI-powered grading',
                'Plagiarism detection',
                'Gamification',
                'Real-time collaboration',
            ],
        },
        'v2': {
            'version': 'v2',
            'api_version': '2.0.0',
            'status': 'stable',
            'endpoints': {
                'auth': '/api/v2/auth',
                'submissions': '/api/v2/submissions',
                'assignments': '/api/v2/assignments',
                'gamification': '/api/v2/gamification',
                'plagiarism': '/api/v2/plagiarism',
                'collaboration': '/api/v2/collaboration',
                'analytics': '/api/v2/analytics',
            },
            'features': [
                'AI-powered grading with GPT-4',
                'Cross-language plagiarism detection',
                'Advanced gamification with achievements',
                'Real-time collaboration with video',
                'Predictive analytics',
                'Smart assignment generation',
            ],
            'breaking_changes': [
                'Authentication now requires JWT tokens',
                'Submission format updated with metrics',
                'New analytics endpoints',
            ],
        },
    }
    return versions.get(version, versions['v1'])


def require_api_version(min_version='v1'):
    """Decorator to require minimum API version.

    Args:
        min_version: Minimum required API version ('v1' or 'v2')

    Returns:
        Decorator function
    """
    from functools import wraps

    version_order = {'v1': 1, 'v2': 2}

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_version = get_api_version()
            current_order = version_order.get(current_version, 1)
            min_order = version_order.get(min_version, 1)

            if current_order < min_order:
                return jsonify({
                    'error': 'API version too old',
                    'message': f'This endpoint requires API version {min_version} or higher',
                    'required_version': min_version,
                    'current_version': current_version,
                    'upgrade_url': '/api/docs#versioning'
                }), 400

            return func(*args, **kwargs)

        return wrapper

    return decorator


def add_version_headers(response, version=None):
    """Add API version headers to response.

    Args:
        response: Flask response object
        version: Optional version string. If None, detects from request.

    Returns:
        Response with version headers added
    """
    if version is None:
        version = get_api_version()

    version_info = get_api_version_info(version)
    response.headers['X-API-Version'] = version_info['api_version']
    response.headers['X-API-Status'] = version_info['status']

    return response
