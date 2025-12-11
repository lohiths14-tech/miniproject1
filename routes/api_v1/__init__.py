"""
API Version 1 Blueprints Package

This package contains all v1 API endpoints that wrap existing functionality
with versioned URL prefixes for backward compatibility.
"""

from flask import Blueprint

# Create main v1 blueprint
api_v1_bp = Blueprint('api_v1_main', __name__, url_prefix='/api/v1')

# Import and register sub-blueprints
from .auth import auth_v1_bp
from .submissions import submissions_v1_bp
from .assignments import assignments_v1_bp
from .gamification import gamification_v1_bp
from .plagiarism import plagiarism_v1_bp
from .collaboration import collaboration_v1_bp

__all__ = [
    'api_v1_bp',
    'auth_v1_bp',
    'submissions_v1_bp',
    'assignments_v1_bp',
    'gamification_v1_bp',
    'plagiarism_v1_bp',
    'collaboration_v1_bp',
]
