"""
Feature Flags for Production Readiness
Enables gradual rollout and A/B testing
"""
import os
from functools import wraps
from typing import Any, Dict

from flask import abort, request


class FeatureFlags:
    """
    Centralized feature flag management.

    Usage:
        if feature_flags.is_enabled('new_ui'):
            # Show new UI

        @feature_required('ml_grading')
        def ml_endpoint():
            # ML-powered endpoint
    """

    def __init__(self):
        self.flags = self._load_flags()

    def _load_flags(self) -> Dict[str, bool]:
        """Load feature flags from environment variables."""
        return {
            # UI Features
            "new_ui": self._parse_bool(os.environ.get("FEATURE_NEW_UI", "false")),
            "dark_mode": self._parse_bool(os.environ.get("FEATURE_DARK_MODE", "true")),
            "pwa": self._parse_bool(os.environ.get("FEATURE_PWA", "false")),
            # Advanced Features
            "ml_grading": self._parse_bool(os.environ.get("FEATURE_ML_GRADING", "false")),
            "cross_language_plagiarism": self._parse_bool(
                os.environ.get("FEATURE_CROSS_LANG", "true")
            ),
            "real_time_collaboration": self._parse_bool(os.environ.get("FEATURE_COLLAB", "true")),
            # Performance Features
            "cdn": self._parse_bool(os.environ.get("FEATURE_CDN", "false")),
            "compression": self._parse_bool(os.environ.get("FEATURE_COMPRESSION", "true")),
            "caching": self._parse_bool(os.environ.get("FEATURE_CACHING", "true")),
            # Security Features
            "rate_limiting": self._parse_bool(os.environ.get("FEATURE_RATE_LIMIT", "true")),
            "api_key_auth": self._parse_bool(os.environ.get("FEATURE_API_KEY", "false")),
            "encryption": self._parse_bool(os.environ.get("FEATURE_ENCRYPTION", "false")),
        }

    def _parse_bool(self, value: str) -> bool:
        """Parse string to boolean."""
        return value.lower() in ("true", "1", "yes", "on")

    def is_enabled(self, feature: str) -> bool:
        """
        Check if a feature is enabled.

        Args:
            feature: Feature flag name

        Returns:
            True if feature is enabled
        """
        return self.flags.get(feature, False)

    def enable(self, feature: str):
        """Enable a feature flag (runtime)."""
        self.flags[feature] = True

    def disable(self, feature: str):
        """Disable a feature flag (runtime)."""
        self.flags[feature] = False

    def get_all(self) -> Dict[str, bool]:
        """Get all feature flags."""
        return self.flags.copy()


# Global instance
feature_flags = FeatureFlags()


def feature_required(feature_name: str):
    """
    Decorator to require a feature flag for an endpoint.

    Usage:
        @app.route('/new-feature')
        @feature_required('new_ui')
        def new_feature():
            return "New feature!"
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not feature_flags.is_enabled(feature_name):
                abort(404)  # Feature not available
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def feature_variant(feature_name: str, variants: Dict[str, Any]):
    """
    A/B testing support.

    Usage:
        @feature_variant('ui_test', {'a': old_ui, 'b': new_ui})
        def get_ui(variant):
            return variant()
    """

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple hash-based variant selection
            user_id = request.args.get("user_id", "default")
            variant_key = "a" if hash(user_id) % 2 == 0 else "b"
            variant = variants.get(variant_key)
            return f(variant, *args, **kwargs)

        return decorated_function

    return decorator
