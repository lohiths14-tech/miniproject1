"""Distributed Tracing Service.

This module provides OpenTelemetry integration with Jaeger for distributed
request tracing across the AI Grading System.
"""

import logging
from functools import wraps

from flask import request

try:
    from opentelemetry import trace
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor

    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    trace = None
    JaegerExporter = None
    FlaskInstrumentor = None
    PymongoInstrumentor = None
    RequestsInstrumentor = None
    Resource = None
    TracerProvider = None
    BatchSpanProcessor = None

logger = logging.getLogger(__name__)

# Global tracer
tracer = None


def init_tracing(app, service_name="ai-grading-system"):
    """Initialize OpenTelemetry tracing with Jaeger exporter.

    Args:
        app: Flask application instance
        service_name: Name of the service for tracing

    Returns:
        Tracer instance or None if initialization fails
    """
    global tracer  # pylint: disable=global-statement

    if not TRACING_AVAILABLE:
        logger.warning("OpenTelemetry not available - tracing disabled")
        return None

    try:
        # Create resource with service information
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": "2.0.0",
                "deployment.environment": app.config.get("FLASK_ENV", "development"),
            }
        )

        # Set up tracer provider
        provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(provider)

        # Configure Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=app.config.get("JAEGER_AGENT_HOST", "localhost"),
            agent_port=app.config.get("JAEGER_AGENT_PORT", 6831),
        )

        # Add span processor
        provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

        # Get tracer
        tracer = trace.get_tracer(__name__)

        # Instrument Flask app
        FlaskInstrumentor().instrument_app(app)

        # Instrument requests library
        RequestsInstrumentor().instrument()

        # Instrument PyMongo
        try:
            PymongoInstrumentor().instrument()
        except (ValueError, KeyError, AttributeError, ImportError) as error:
            logger.warning("PyMongo instrumentation failed: %s", error)

        # Add custom span processor for additional context
        provider.add_span_processor(CustomSpanProcessor())

        logger.info(
            "✅ Distributed tracing initialized - Jaeger at %s:6831",
            app.config.get("JAEGER_AGENT_HOST", "localhost"),
        )

        return tracer

    except (ValueError, KeyError, AttributeError, ImportError) as error:
        logger.error("Failed to initialize tracing: %s", error)
        return None


class CustomSpanProcessor:
    """Custom span processor to add additional context to traces."""

    def on_start(self, span, parent_context):
        """Called when span starts.

        Args:
            span: The span that is starting
            parent_context: Parent context
        """
        # Add custom attributes here if needed
        return

    def on_end(self, span):
        """Called when span ends.

        Args:
            span: The span that is ending
        """
        # Add custom processing here if needed
        return

    def shutdown(self):
        """Shutdown processor and cleanup resources."""
        # Cleanup if needed
        return

    def force_flush(self, timeout_millis=30000):
        """Force flush spans.

        Args:
            timeout_millis: Timeout in milliseconds

        Returns:
            bool: True if successful
        """
        return True


def trace_function(operation_name=None):
    """Decorator to add tracing to a function.

    Args:
        operation_name: Optional custom name for the trace span

    Returns:
        Decorated function with tracing enabled

    Usage:
        @trace_function("grade_submission")
        def grade_submission(code, test_cases):
            # Your function logic
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not tracer:
                return func(*args, **kwargs)

            span_name = operation_name or f"{func.__module__}.{func.__name__}"

            with tracer.start_as_current_span(span_name) as span:
                # Add function arguments as attributes (if not sensitive)
                if args:
                    span.set_attribute("args.count", len(args))
                if kwargs:
                    span.set_attribute("kwargs.count", len(kwargs))

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except (ValueError, KeyError, AttributeError, ImportError) as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise

        return wrapper

    return decorator


def trace_database_query(collection_name, operation):
    """Decorator to add tracing to database queries.

    Args:
        collection_name: Name of the MongoDB collection
        operation: Type of operation (find, insert, update, delete)

    Returns:
        Decorated function with database tracing

    Usage:
        @trace_database_query("submissions", "find")
        def get_submissions():
            # Your query logic
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not tracer:
                return func(*args, **kwargs)

            with tracer.start_as_current_span(f"db.{collection_name}.{operation}") as span:
                span.set_attribute("db.system", "mongodb")
                span.set_attribute("db.name", "ai_grading")
                span.set_attribute("db.collection", collection_name)
                span.set_attribute("db.operation", operation)

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)
                    return result
                except (ValueError, KeyError, AttributeError, ImportError) as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    raise

        return wrapper

    return decorator


def trace_ai_request(model_name="gpt-3.5-turbo"):
    """Decorator to add tracing to AI API requests.

    Args:
        model_name: Name of the AI model being used

    Returns:
        Decorated function with AI request tracing

    Usage:
        @trace_ai_request("gpt-3.5-turbo")
        def call_openai_api():
            # Your API call logic
            pass
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not tracer:
                return func(*args, **kwargs)

            with tracer.start_as_current_span("ai.request") as span:
                span.set_attribute("ai.model", model_name)
                span.set_attribute("ai.provider", "openai")

                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("success", True)

                    # Add token usage if available
                    if isinstance(result, dict) and "usage" in result:
                        span.set_attribute(
                            "ai.tokens.prompt", result["usage"].get("prompt_tokens", 0)
                        )
                        span.set_attribute(
                            "ai.tokens.completion", result["usage"].get("completion_tokens", 0)
                        )
                        span.set_attribute(
                            "ai.tokens.total", result["usage"].get("total_tokens", 0)
                        )

                    return result
                except (ValueError, KeyError, AttributeError, ImportError) as e:
                    span.set_attribute("success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    raise

        return wrapper

    return decorator


def add_span_attributes(**attributes):
    """
    Add custom attributes to current span

    Usage:
        add_span_attributes(user_id="123", assignment_id="456")
    """
    if not tracer:
        return

    current_span = trace.get_current_span()
    if current_span:
        for key, value in attributes.items():
            current_span.set_attribute(key, value)


def add_span_event(name, attributes=None):
    """
    Add an event to the current span

    Usage:
        add_span_event("code_executed", {"language": "python", "time_ms": 123})
    """
    if not tracer:
        return

    current_span = trace.get_current_span()
    if current_span:
        current_span.add_event(name, attributes or {})


def create_child_span(name):
    """
    Create a child span for complex operations

    Usage:
        with create_child_span("plagiarism_check"):
            # Do plagiarism check
    """
    if not tracer:
        # Return a no-op context manager
        from contextlib import nullcontext

        return nullcontext()

    return tracer.start_as_current_span(name)


# Middleware to add request context to traces
def add_request_context_to_trace():
    """Add HTTP request context to current trace"""
    if not tracer:
        return

    current_span = trace.get_current_span()
    if not current_span:
        return

    # Add request information
    current_span.set_attribute("http.method", request.method)
    current_span.set_attribute("http.url", request.url)
    current_span.set_attribute("http.user_agent", request.headers.get("User-Agent", ""))

    # Add user context if available
    from flask import session

    if "user_id" in session:
        current_span.set_attribute("user.id", session["user_id"])
    if "role" in session:
        current_span.set_attribute("user.role", session["role"])


# Example usage in services
@trace_function("grade_submission")
def example_grade_with_tracing(code, test_cases):
    """Example of traced function"""
    add_span_attributes(language="python", test_case_count=len(test_cases))

    # Create child spans for sub-operations
    with create_child_span("execute_code"):
        # Execute code
        add_span_event("code_started")
        # ... execution logic
        add_span_event("code_completed", {"execution_time_ms": 123})

    with create_child_span("ai_evaluation"):
        # AI grading
        pass

    return {"score": 95}
