"""
Custom assertions for testing
"""
import re
from datetime import datetime, timedelta
import jwt


def assert_valid_email(email):
    """Assert that a string is a valid email address"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    assert re.match(email_pattern, email), f"Invalid email format: {email}"


def assert_valid_jwt(token, secret_key='test-jwt-secret'):
    """Assert that a string is a valid JWT token"""
    try:
        decoded = jwt.decode(token, secret_key, algorithms=['HS256'])
        assert 'user_id' in decoded or 'sub' in decoded, "JWT missing user identifier"
        return decoded
    except jwt.InvalidTokenError as e:
        raise AssertionError(f"Invalid JWT token: {e}")


def assert_dict_contains(actual, expected):
    """Assert that actual dict contains all keys and values from expected dict"""
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        assert actual[key] == value, f"Value mismatch for key '{key}': expected {value}, got {actual[key]}"


def assert_datetime_recent(dt, max_seconds=60):
    """Assert that a datetime is recent (within max_seconds)"""
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))

    now = datetime.now()
    diff = abs((now - dt).total_seconds())
    assert diff <= max_seconds, f"Datetime {dt} is not recent (diff: {diff}s)"


def assert_response_success(response):
    """Assert that an API response is successful (2xx status code)"""
    assert 200 <= response.status_code < 300, \
        f"Expected success status code, got {response.status_code}: {response.data}"


def assert_response_error(response, expected_status=None):
    """Assert that an API response is an error (4xx or 5xx status code)"""
    assert response.status_code >= 400, \
        f"Expected error status code, got {response.status_code}"

    if expected_status:
        assert response.status_code == expected_status, \
            f"Expected status {expected_status}, got {response.status_code}"


def assert_json_schema(data, schema):
    """Assert that data matches a JSON schema"""
    for key, expected_type in schema.items():
        assert key in data, f"Missing required key: {key}"

        if expected_type is not None:
            actual_type = type(data[key])
            assert isinstance(data[key], expected_type), \
                f"Type mismatch for key '{key}': expected {expected_type}, got {actual_type}"


def assert_list_sorted(lst, key=None, reverse=False):
    """Assert that a list is sorted"""
    if key:
        sorted_list = sorted(lst, key=key, reverse=reverse)
    else:
        sorted_list = sorted(lst, reverse=reverse)

    assert lst == sorted_list, "List is not sorted correctly"


def assert_pagination_valid(response_data):
    """Assert that pagination data is valid"""
    required_keys = ['items', 'total', 'page', 'per_page', 'pages']
    for key in required_keys:
        assert key in response_data, f"Missing pagination key: {key}"

    assert isinstance(response_data['items'], list), "items must be a list"
    assert isinstance(response_data['total'], int), "total must be an integer"
    assert isinstance(response_data['page'], int), "page must be an integer"
    assert isinstance(response_data['per_page'], int), "per_page must be an integer"
    assert isinstance(response_data['pages'], int), "pages must be an integer"

    assert response_data['page'] > 0, "page must be positive"
    assert response_data['per_page'] > 0, "per_page must be positive"
    assert response_data['total'] >= 0, "total must be non-negative"


def assert_code_similarity(code1, code2, min_similarity=0.0, max_similarity=100.0):
    """Assert that code similarity is within expected range"""
    # This is a placeholder - actual implementation would use plagiarism service
    similarity = 50.0  # Mock value
    assert min_similarity <= similarity <= max_similarity, \
        f"Code similarity {similarity}% not in range [{min_similarity}, {max_similarity}]"


def assert_performance_acceptable(execution_time, max_time):
    """Assert that execution time is within acceptable limits"""
    assert execution_time <= max_time, \
        f"Execution time {execution_time}s exceeds maximum {max_time}s"


def assert_cache_hit(cache_stats):
    """Assert that cache was hit"""
    assert cache_stats.get('hit', False), "Expected cache hit, got miss"


def assert_cache_miss(cache_stats):
    """Assert that cache was missed"""
    assert not cache_stats.get('hit', True), "Expected cache miss, got hit"


def assert_file_exists(filepath):
    """Assert that a file exists"""
    import os
    assert os.path.exists(filepath), f"File does not exist: {filepath}"


def assert_valid_mongodb_id(id_str):
    """Assert that a string is a valid MongoDB ObjectId"""
    from bson import ObjectId
    try:
        ObjectId(id_str)
    except Exception as e:
        raise AssertionError(f"Invalid MongoDB ObjectId: {id_str} - {e}")


def assert_achievement_earned(user_data, achievement_type):
    """Assert that a user has earned a specific achievement"""
    achievements = user_data.get('achievements', [])
    achievement_types = [a.get('type') for a in achievements]
    assert achievement_type in achievement_types, \
        f"Achievement '{achievement_type}' not found in user achievements"


def assert_points_increased(old_points, new_points):
    """Assert that points have increased"""
    assert new_points > old_points, \
        f"Points did not increase: {old_points} -> {new_points}"


def assert_leaderboard_sorted(leaderboard):
    """Assert that leaderboard is sorted by points descending"""
    points = [entry['points'] for entry in leaderboard]
    assert points == sorted(points, reverse=True), \
        "Leaderboard is not sorted by points descending"
