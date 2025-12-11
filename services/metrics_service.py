# Prometheus Metrics Exporter for AI Grading System
# Provides detailed metrics for monitoring and alerting

import time
from functools import wraps

from flask import Response
from prometheus_client import Counter, Gauge, Histogram, Summary, generate_latest

# Counters
submissions_total = Counter(
    "submissions_total", "Total number of code submissions", ["language", "status"]
)

plagiarism_checks_total = Counter(
    "plagiarism_checks_total", "Total plagiarism checks performed", ["result"]
)

user_registrations_total = Counter("user_registrations_total", "Total user registrations", ["role"])

# Histograms
grading_duration_seconds = Histogram(
    "grading_duration_seconds",
    "Time spent grading submissions",
    ["language"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
)

plagiarism_check_duration_seconds = Histogram(
    "plagiarism_check_duration_seconds",
    "Time spent checking plagiarism",
    buckets=[0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 30.0],
)

api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "API request duration",
    ["method", "endpoint", "status"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# Gauges
active_users = Gauge("active_users", "Number of currently active users", ["role"])

pending_submissions = Gauge("pending_submissions", "Number of pending submissions")

cache_hit_ratio = Gauge("cache_hit_ratio", "Redis cache hit ratio")

database_connections = Gauge(
    "database_connections", "Number of active database connections", ["state"]
)

# Summary
code_quality_score = Summary("code_quality_score", "Code quality scores distribution")

similarity_scores = Summary("similarity_scores", "Plagiarism similarity scores distribution")


# Decorators for automatic metrics
def track_submission(language="python"):
    """Decorator to track submission metrics"""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time

                # Record metrics
                submissions_total.labels(language=language, status="success").inc()
                grading_duration_seconds.labels(language=language).observe(duration)

                # Track quality score if available
                if isinstance(result, dict) and "score" in result:
                    code_quality_score.observe(result["score"])

                return result
            except Exception as e:
                submissions_total.labels(language=language, status="error").inc()
                raise

        return wrapper

    return decorator


def track_api_request(endpoint_name):
    """Decorator to track API request metrics"""

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            from flask import request

            start_time = time.time()

            try:
                result = f(*args, **kwargs)
                duration = time.time() - start_time

                status = (
                    getattr(result, "status_code", 200) if hasattr(result, "status_code") else 200
                )

                api_request_duration_seconds.labels(
                    method=request.method, endpoint=endpoint_name, status=status
                ).observe(duration)

                return result
            except Exception as e:
                duration = time.time() - start_time
                api_request_duration_seconds.labels(
                    method=request.method, endpoint=endpoint_name, status=500
                ).observe(duration)
                raise

        return wrapper

    return decorator


# Metrics endpoint
def metrics_endpoint():
    """Expose metrics for Prometheus scraping"""
    return Response(generate_latest(), mimetype="text/plain")


# Helper functions
def record_plagiarism_check(result, duration, similarity_score):
    """Record plagiarism check metrics"""
    plagiarism_checks_total.labels(result=result).inc()
    plagiarism_check_duration_seconds.observe(duration)
    if similarity_score is not None:
        similarity_scores.observe(similarity_score)


def update_active_users(role, count):
    """Update active users gauge"""
    active_users.labels(role=role).set(count)


def update_pending_submissions(count):
    """Update pending submissions gauge"""
    pending_submissions.set(count)


def update_cache_metrics(hits, misses):
    """Update cache hit ratio"""
    total = hits + misses
    ratio = hits / total if total > 0 else 0
    cache_hit_ratio.set(ratio)
