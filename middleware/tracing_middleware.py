"""Tracing Middleware for Flask Applications.

This module provides middleware to automatically add distributed tracing
to Flask requests using OpenTelemetry.
"""

import logging
import time

from flask import g

try:
    from services.tracing_service import add_span_attributes, add_span_event, tracer
except ImportError:
    # Graceful fallback if tracing service is not available
    tracer = None
    add_span_attributes = lambda **kwargs: None
    add_span_event = lambda name, attrs: None

logger = logging.getLogger(__name__)


def init_tracing_middleware(app):
    """Initialize tracing middleware for Flask application.

    Args:
        app: Flask application instance

    This middleware adds distributed tracing to all requests, capturing:
    - Request duration
    - HTTP status codes
    - Response sizes
    - Error events for 4xx/5xx responses
    """

    @app.before_request
    def before_request():
        """Add tracing context before each request."""
        g.start_time = time.time()

    @app.after_request
    def after_request(response):
        """Add tracing information after each request.

        Args:
            response: Flask response object

        Returns:
            Flask response object with tracing information added
        """
        if not tracer:
            return response

        try:
            # Calculate request duration
            duration = time.time() - g.get("start_time", time.time())

            # Add attributes to current span
            add_span_attributes(
                http_status_code=response.status_code, http_duration_ms=int(duration * 1000)
            )

            # Add events for important status codes
            if response.status_code >= 400:
                add_span_event("error_response", {"status_code": response.status_code})

            # Add response size
            if response.content_length:
                add_span_attributes(http_response_size_bytes=response.content_length)

        except (AttributeError, ValueError) as error:
            logger.warning("Failed to add tracing info: %s", error)

        return response

    logger.info("✅ Tracing middleware initialized")


def trace_route(route_name=None):
    """Decorator to add custom tracing to routes.

    Args:
        route_name: Optional custom name for the trace span

    Returns:
        Decorated function with tracing enabled

    Usage:
        @app.route('/api/submissions/submit')
        @trace_route("submit_assignment")
        def submit_assignment():
            # Your route logic here
            pass
    """

    def decorator(func):
        """Inner decorator function."""
        try:
            from services.tracing_service import trace_function

            # Use the trace_function decorator
            return trace_function(route_name)(func)
        except ImportError:
            # If tracing service not available, return original function
            return func

    return decorator
