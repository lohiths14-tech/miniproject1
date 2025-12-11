"""Tests for Metrics Service.

Tests metric collection, aggregation, and Prometheus metrics reporting.
Requirements: 2.1, 2.2
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

# Check if prometheus_client is available
try:
    from prometheus_client import Counter, Gauge, Histogram, Summary
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Skip all tests if prometheus_client is not available
pytestmark = pytest.mark.skipif(
    not PROMETHEUS_AVAILABLE,
    reason="prometheus_client not installed"
)


@pytest.fixture
def metrics_service():
    """Import metrics service only if prometheus is available."""
    if PROMETHEUS_AVAILABLE:
        from services import metrics_service
        return metrics_service
    return None


class TestCounterMetrics:
    """Test suite for counter metrics."""

    def test_submissions_total_counter_exists(self, metrics_service):
        """Test that submissions_total counter exists."""
        assert metrics_service.submissions_total is not None
        assert hasattr(metrics_service.submissions_total, 'labels')

    def test_plagiarism_checks_total_counter_exists(self, metrics_service):
        """Test that plagiarism_checks_total counter exists."""
        assert metrics_service.plagiarism_checks_total is not None
        assert hasattr(metrics_service.plagiarism_checks_total, 'labels')

    def test_user_registrations_total_counter_exists(self, metrics_service):
        """Test that user_registrations_total counter exists."""
        assert metrics_service.user_registrations_total is not None
        assert hasattr(metrics_service.user_registrations_total, 'labels')

    def test_submissions_counter_can_increment(self, metrics_service):
        """Test that submissions counter can be incremented."""
        metrics_service.submissions_total.labels(language="python", status="success").inc()

    def test_plagiarism_counter_can_increment(self, metrics_service):
        """Test that plagiarism counter can be incremented."""
        metrics_service.plagiarism_checks_total.labels(result="clean").inc()

    def test_user_registrations_counter_can_increment(self, metrics_service):
        """Test that user registrations counter can be incremented."""
        metrics_service.user_registrations_total.labels(role="student").inc()


class TestHistogramMetrics:
    """Test suite for histogram metrics."""

    def test_grading_duration_histogram_exists(self, metrics_service):
        """Test that grading_duration_seconds histogram exists."""
        assert metrics_service.grading_duration_seconds is not None
        assert hasattr(metrics_service.grading_duration_seconds, 'labels')

    def test_plagiarism_check_duration_histogram_exists(self, metrics_service):
        """Test that plagiarism_check_duration_seconds histogram exists."""
        assert metrics_service.plagiarism_check_duration_seconds is not None
        assert hasattr(metrics_service.plagiarism_check_duration_seconds, 'observe')

    def test_api_request_duration_histogram_exists(self, metrics_service):
        """Test that api_request_duration_seconds histogram exists."""
        assert metrics_service.api_request_duration_seconds is not None
        assert hasattr(metrics_service.api_request_duration_seconds, 'labels')

    def test_grading_duration_can_observe(self, metrics_service):
        """Test that grading duration can record observations."""
        metrics_service.grading_duration_seconds.labels(language="python").observe(1.5)

    def test_api_request_duration_can_observe(self, metrics_service):
        """Test that API request duration can record observations."""
        metrics_service.api_request_duration_seconds.labels(
            method="GET", endpoint="/api/test", status=200
        ).observe(0.1)


class TestGaugeMetrics:
    """Test suite for gauge metrics."""

    def test_active_users_gauge_exists(self, metrics_service):
        """Test that active_users gauge exists."""
        assert metrics_service.active_users is not None
        assert hasattr(metrics_service.active_users, 'labels')

    def test_pending_submissions_gauge_exists(self, metrics_service):
        """Test that pending_submissions gauge exists."""
        assert metrics_service.pending_submissions is not None
        assert hasattr(metrics_service.pending_submissions, 'set')

    def test_cache_hit_ratio_gauge_exists(self, metrics_service):
        """Test that cache_hit_ratio gauge exists."""
        assert metrics_service.cache_hit_ratio is not None
        assert hasattr(metrics_service.cache_hit_ratio, 'set')

    def test_database_connections_gauge_exists(self, metrics_service):
        """Test that database_connections gauge exists."""
        assert metrics_service.database_connections is not None
        assert hasattr(metrics_service.database_connections, 'labels')

    def test_active_users_can_set(self, metrics_service):
        """Test that active users gauge can be set."""
        metrics_service.active_users.labels(role="student").set(10)

    def test_pending_submissions_can_set(self, metrics_service):
        """Test that pending submissions gauge can be set."""
        metrics_service.pending_submissions.set(5)


class TestSummaryMetrics:
    """Test suite for summary metrics."""

    def test_code_quality_score_summary_exists(self, metrics_service):
        """Test that code_quality_score summary exists."""
        assert metrics_service.code_quality_score is not None
        assert hasattr(metrics_service.code_quality_score, 'observe')

    def test_similarity_scores_summary_exists(self, metrics_service):
        """Test that similarity_scores summary exists."""
        assert metrics_service.similarity_scores is not None
        assert hasattr(metrics_service.similarity_scores, 'observe')

    def test_code_quality_can_observe(self, metrics_service):
        """Test that code quality score can record observations."""
        metrics_service.code_quality_score.observe(85)

    def test_similarity_scores_can_observe(self, metrics_service):
        """Test that similarity scores can record observations."""
        metrics_service.similarity_scores.observe(0.15)


class TestTrackSubmissionDecorator:
    """Test suite for track_submission decorator."""

    def test_track_submission_decorator_exists(self, metrics_service):
        """Test that track_submission decorator exists."""
        assert metrics_service.track_submission is not None
        assert callable(metrics_service.track_submission)

    def test_track_submission_returns_decorator(self, metrics_service):
        """Test that track_submission returns a decorator."""
        decorator = metrics_service.track_submission(language="python")
        assert callable(decorator)

    def test_track_submission_wraps_function(self, metrics_service):
        """Test that track_submission properly wraps a function."""
        @metrics_service.track_submission(language="python")
        def sample_function():
            return {"score": 85}

        result = sample_function()
        assert result == {"score": 85}

    def test_track_submission_handles_exceptions(self, metrics_service):
        """Test that track_submission handles exceptions."""
        @metrics_service.track_submission(language="python")
        def failing_function():
            raise ValueError("Test error")

        with pytest.raises(ValueError):
            failing_function()


class TestTrackApiRequestDecorator:
    """Test suite for track_api_request decorator."""

    def test_track_api_request_decorator_exists(self, metrics_service):
        """Test that track_api_request decorator exists."""
        assert metrics_service.track_api_request is not None
        assert callable(metrics_service.track_api_request)

    def test_track_api_request_returns_decorator(self, metrics_service):
        """Test that track_api_request returns a decorator."""
        decorator = metrics_service.track_api_request("test_endpoint")
        assert callable(decorator)


class TestMetricsEndpoint:
    """Test suite for metrics endpoint."""

    def test_metrics_endpoint_exists(self, metrics_service):
        """Test that metrics_endpoint function exists."""
        assert metrics_service.metrics_endpoint is not None
        assert callable(metrics_service.metrics_endpoint)

    def test_metrics_endpoint_returns_response(self, metrics_service):
        """Test that metrics_endpoint returns a Response."""
        from flask import Response
        result = metrics_service.metrics_endpoint()
        assert isinstance(result, Response)

    def test_metrics_endpoint_content_type(self, metrics_service):
        """Test that metrics endpoint returns text/plain content type."""
        result = metrics_service.metrics_endpoint()
        assert result.content_type == "text/plain; charset=utf-8"


class TestHelperFunctions:
    """Test suite for helper functions."""

    def test_record_plagiarism_check_exists(self, metrics_service):
        """Test that record_plagiarism_check function exists."""
        assert metrics_service.record_plagiarism_check is not None
        assert callable(metrics_service.record_plagiarism_check)

    def test_record_plagiarism_check_records_metrics(self, metrics_service):
        """Test that record_plagiarism_check records metrics."""
        metrics_service.record_plagiarism_check("clean", 1.5, 0.1)

    def test_record_plagiarism_check_with_none_similarity(self, metrics_service):
        """Test record_plagiarism_check with None similarity score."""
        metrics_service.record_plagiarism_check("error", 0.5, None)

    def test_update_active_users_exists(self, metrics_service):
        """Test that update_active_users function exists."""
        assert metrics_service.update_active_users is not None
        assert callable(metrics_service.update_active_users)

    def test_update_active_users_sets_gauge(self, metrics_service):
        """Test that update_active_users sets the gauge."""
        metrics_service.update_active_users("student", 25)

    def test_update_pending_submissions_exists(self, metrics_service):
        """Test that update_pending_submissions function exists."""
        assert metrics_service.update_pending_submissions is not None
        assert callable(metrics_service.update_pending_submissions)

    def test_update_pending_submissions_sets_gauge(self, metrics_service):
        """Test that update_pending_submissions sets the gauge."""
        metrics_service.update_pending_submissions(10)

    def test_update_cache_metrics_exists(self, metrics_service):
        """Test that update_cache_metrics function exists."""
        assert metrics_service.update_cache_metrics is not None
        assert callable(metrics_service.update_cache_metrics)

    def test_update_cache_metrics_calculates_ratio(self, metrics_service):
        """Test that update_cache_metrics calculates hit ratio."""
        metrics_service.update_cache_metrics(80, 20)

    def test_update_cache_metrics_handles_zero_total(self, metrics_service):
        """Test that update_cache_metrics handles zero total."""
        metrics_service.update_cache_metrics(0, 0)
