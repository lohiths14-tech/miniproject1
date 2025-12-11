"""
API Version 2 Blueprints Package

This package contains all v2 API endpoints with enhanced features,
improved response formats, and new capabilities like analytics.
"""

from flask import Blueprint

# Create main v2 blueprint
api_v2_bp = Blueprint('api_v2_main', __name__, url_prefix='/api/v2')

# Import and register sub-blueprints
from .auth import auth_v2_bp
from .submissions import submissions_v2_bp
from .assignments import assignments_v2_bp
from .gamification import gamification_v2_bp
from .plagiarism import plagiarism_v2_bp
from .collaboration import collaboration_v2_bp
from .analytics import analytics_v2_bp

__all__ = [
    'api_v2_bp',
    'auth_v2_bp',
    'submissions_v2_bp',
    'assignments_v2_bp',
    'gamification_v2_bp',
    'plagiarism_v2_bp',
    'collaboration_v2_bp',
    'analytics_v2_bp',
]
