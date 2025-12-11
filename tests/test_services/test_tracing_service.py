"""Tests for Tracing Service.

Tests distributed tracing, span management, and OpenTelemetry integration.
Requirements: 2.1, 2.2
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from contextlib import nullcontext

from services.tracing_service import (
    TRACING_AVAILABLE,
    CustomSpanProcessor,
    trace_function,
    trace_database_query,
    trace_ai_request,
    add_span_attributes,
    add_span_event,
    create_child_span,
)


class TestTracingAvailability:
    """Test suite for tracing availability check."""

    def test_tracing_available_is_boolean(self):
        """Test that TRACING_AVAILABLE is a boolean."""
        assert isinstance(TRACING_AVAILABLE, bool)


class TestCustomSpanProcessor:
    """Test suite for CustomSpanProcessor."""

    def test_custom_span_processor_instantiation(self):
        """Test that CustomSpanProcessor can be instantiated."""
        processor = CustomSpanProcessor()
        assert processor is not None

    def test_on_start_method_exists(self):
        """Test that on_start method exists."""
        processor = CustomSpanProcessor()
        assert hasattr(processor, 'on_start')
        assert callable(processor.on_start)

    def test_on_end_method_exists(self):
        """Test that on_end method exists."""
        processor = CustomSpanProcessor()
        assert hasattr(processor, 'on_end')
        assert callable(processor.on_end)

    def test_shutdown_method_exists(self):
        """Test that shutdown method exists."""
        processor = CustomSpanProcessor()
        assert hasattr(processor, 'shutdown')
        assert callable(processor.shutdown)

    def test_force_flush_method_exists(self):
        """Test that force_flush method exists."""
        processor = CustomSpanProcessor()
        assert hasattr(processor, 'force_flush')
        assert callable(processor.force_flush)

    def test_on_start_accepts_span_and_context(self):
        """Test that on_start accepts span and parent_context."""
        processor = CustomSpanProcessor()
        mock_span = Mock()
        mock_context = Mock()
        # Should not raise
        processor.on_start(mock_span, mock_context)

    def test_on_end_accepts_span(self):
        """Test that on_end accepts span."""
        processor = CustomSpanProcessor()
        mock_span = Mock()
        # Should not raise
        processor.on_end(mock_span)

    def test_shutdown_completes(self):
        """Test that shutdown completes without error."""
        processor = CustomSpanProcessor()
        # Should not raise
        processor.shutdown()

    def test_force_flush_returns_true(self):
        """Test that force_flush returns True."""
        processor = CustomSpanProcessor()
        result = processor.force_flush()
        assert result is True

    def test_force_flush_accepts_timeout(self):
        """Test that force_flush accepts timeout parameter."""
        processor = CustomSpanProcessor()
        result = processor.force_flush(timeout_millis=5000)
        assert result is True


class TestTraceFunctionDecorator:
    """Test suite for trace_function decorator."""

    def test_trace_function_exists(self):
        """Test that trace_function decorator exists."""
        assert trace_function is not None
        assert callable(trace_function)

    def test_trace_function_returns_decorator(self):
        """Test that trace_function returns a decorator."""
        decorator = trace_function("test_operation")
        assert callable(decorator)

    def test_trace_function_wraps_function(self):
        """Test that trace_function properly wraps a function."""
        @trace_function("test_operation")
        def sample_function(x, y):
            return x + y

        result = sample_function(2, 3)
        assert result == 5

    def test_trace_function_preserves_return_value(self):
        """Test that trace_function preserves function return value."""
        @trace_function()
        def return_dict():
            return {"key": "value"}

        result = return_dict()
        assert result == {"key": "value"}

    def test_trace_function_handles_exceptions(self):
        """Test that trace_function re-raises exceptions."""
        @trace_function("failing_operation")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            failing_function()

    def test_trace_function_with_no_args(self):
        """Test trace_function with no operation name."""
        @trace_function()
        def no_name_function():
            return "result"

        result = no_name_function()
        assert result == "result"

    def test_trace_function_with_kwargs(self):
        """Test trace_function with function that uses kwargs."""
        @trace_function("kwargs_operation")
        def kwargs_function(**kwargs):
            return kwargs

        result = kwargs_function(a=1, b=2)
        assert result == {"a": 1, "b": 2}


class TestTraceDatabaseQueryDecorator:
    """Test suite for trace_database_query decorator."""

    def test_trace_database_query_exists(self):
        """Test that trace_database_query decorator exists."""
        assert trace_database_query is not None
        assert callable(trace_database_query)

    def test_trace_database_query_returns_decorator(self):
        """Test that trace_database_query returns a decorator."""
        decorator = trace_database_query("users", "find")
        assert callable(decorator)

    def test_trace_database_query_wraps_function(self):
        """Test that trace_database_query properly wraps a function."""
        @trace_database_query("submissions", "insert")
        def insert_submission(data):
            return {"inserted_id": "123"}

        result = insert_submission({"code": "print('hello')"})
        assert result == {"inserted_id": "123"}

    def test_trace_database_query_handles_exceptions(self):
        """Test that trace_database_query rses exceptions."""
        @trace_database_query("users", "find")
        def failing_query():
            raise KeyError("Document not found")

        with pytest.raises(KeyError):
            failing_query()


class TestTraceAiRequestDecorator:
    """Test suite for trace_ai_request decorator."""

    def test_trace_ai_request_exists(self):
        """Test that trace_ai_request decorator exists."""
        assert trace_ai_request is not None
        assert callable(trace_ai_request)

    def test_trace_ai_request_returns_decorator(self):
        """Test that trace_ai_request returns a decorator."""
        decorator = trace_ai_request("gpt-4")
        assert callable(decorator)

    def test_trace_ai_request_wraps_function(self):
        """Test that trace_ai_request properly wraps a function."""
        @trace_ai_request("gpt-3.5-turbo")
        def call_ai():
            return {"response": "Hello!"}

        result = call_ai()
        assert result == {"response": "Hello!"}

    def test_trace_ai_request_with_usage_info(self):
        """Test trace_ai_request with usage information in result."""
        @trace_ai_request("gpt-4")
        def call_ai_with_usage():
            return {
                "response": "Hello!",
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 5,
                    "total_tokens": 15
                }
            }

        result = call_ai_with_usage()
        assert result["usage"]["total_tokens"] == 15

    def test_trace_ai_request_handles_exceptions(self):
        """Test that trace_ai_request re-raises exceptions."""
        @trace_ai_request("gpt-4")
        def failing_ai_call():
            raise ValueError("API error")

        with pytest.raises(ValueError):
            failing_ai_call()


class TestAddSpanAttributes:
    """Test suite for add_span_attributes function."""

    def test_add_span_attributes_exists(self):
        """Test that add_span_attributes function exists."""
        assert add_span_attributes is not None
        assert callable(add_span_attributes)

    def test_add_span_attributes_accepts_kwargs(self):
        """Test that add_span_attributes accepts keyword arguments."""
        # Should not raise even without active tracer
        add_span_attributes(user_id="123", assignment_id="456")


class TestAddSpanEvent:
    """Test suite for add_span_event function."""

    def test_add_span_event_exists(self):
        """Test that add_span_event function exists."""
        assert add_span_event is not None
        assert callable(add_span_event)

    def test_add_span_event_accepts_name(self):
        """Test that add_span_event accepts event name."""
        # Should not raise even without active tracer
        add_span_event("test_event")

    def test_add_span_event_accepts_attributes(self):
        """Test that add_span_event accepts attributes."""
        # Should not raise even without active tracer
        add_span_event("code_executed", {"language": "python", "time_ms": 123})

    def test_add_span_event_with_none_attributes(self):
        """Test add_span_event with None attributes."""
        # Should not raise
        add_span_event("simple_event", None)


class TestCreateChildSpan:
    """Test suite for create_child_span function."""

    def test_create_child_span_exists(self):
        """Test that create_child_span function exists."""
        assert create_child_span is not None
        assert callable(create_child_span)

    def test_create_child_span_returns_context_manager(self):
        """Test that create_child_span returns a context manager."""
        result = create_child_span("test_span")
        # Should be usable as context manager
        assert hasattr(result, '__enter__') or isinstance(result, nullcontext)

    def test_create_child_span_can_be_used_in_with(self):
        """Test that create_child_span can be used in with statement."""
        with create_child_span("test_operation"):
            # Should not raise
            pass


class TestInitTracing:
    """Test suite for init_tracing function."""

    def test_init_tracing_import(self):
        """Test that init_tracing can be imported."""
        from services.tracing_service import init_tracing
        assert init_tracing is not None
        assert callable(init_tracing)


class TestExampleFunction:
    """Test suite for example traced function."""

    def test_example_grade_with_tracing_exists(self):
        """Test that example_grade_with_tracing function exists."""
        from services.tracing_service import example_grade_with_tracing
        assert example_grade_with_tracing is not None
        assert callable(example_grade_with_tracing)

    def test_example_grade_with_tracing_returns_result(self):
        """Test that example function returns expected result."""
        from services.tracing_service import example_grade_with_tracing
        result = example_grade_with_tracing("print('hello')", [])
        assert result == {"score": 95}

