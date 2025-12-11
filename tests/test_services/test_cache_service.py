"""
Unit Tests for Cache Service (Task 14.1)
Tests Redis operations: get, set, delete, invalidation, and error handling
"""

import json
import pytest
import redis
from unittest.mock import Mock, patch, MagicMock


@pytest.mark.unit
class TestCacheService:
    """Test suite for Cache Service (14.1)"""

    def test_cache_get_operation(self):
        """Test cache get operation (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = '{"data": "test_value"}'

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test get operation
            result = cache.get_cached("test_key")

            assert result == {"data": "test_value"}
            mock_redis_instance.get.assert_called_once_with("test_key")

    def test_cache_get_operation_miss(self):
        """Test cache get operation when key doesn't exist (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = None

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test get operation with cache miss
            result = cache.get_cached("nonexistent_key")

            assert result is None
            mock_redis_instance.get.assert_called_once_with("nonexistent_key")

    def test_cache_set_operation_with_ttl(self):
        """Test cache set operation with TTL (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.setex.return_value = True

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test set operation with custom TTL
            test_data = {"user_id": 123, "name": "Test User"}
            result = cache.cache_result("user:123", test_data, expiration=1800)

            assert result is True
            mock_redis_instance.setex.assert_called_once()
            call_args = mock_redis_instance.setex.call_args
            assert call_args[0][0] == "user:123"
            assert call_args[0][1] == 1800
            assert json.loads(call_args[0][2]) == test_data

    def test_cache_set_operation_default_ttl(self):
        """Test cache set operation with default TTL (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.setex.return_value = True

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test set operation with default TTL (3600)
            test_data = {"score": 95}
            result = cache.cache_result("score:assignment:1", test_data)

            assert result is True
            mock_redis_instance.setex.assert_called_once()
            call_args = mock_redis_instance.setex.call_args
            assert call_args[0][0] == "score:assignment:1"
            assert call_args[0][1] == 3600  # Default TTL

    def test_cache_delete_operation(self):
        """Test cache delete operation (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.delete.return_value = 1

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test delete operation
            result = cache.invalidate("test_key")

            assert result is True
            mock_redis_instance.delete.assert_called_once_with("test_key")

    def test_cache_invalidation_pattern(self):
        """Test cache invalidation with pattern matching (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.keys.return_value = ["user:1", "user:2", "user:3"]
            mock_redis_instance.delete.return_value = 3

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test pattern invalidation
            result = cache.invalidate_pattern("user:*")

            assert result is True
            mock_redis_instance.keys.assert_called_once_with("user:*")
            mock_redis_instance.delete.assert_called_once_with("user:1", "user:2", "user:3")

    def test_cache_invalidation_pattern_no_matches(self):
        """Test cache invalidation when pattern has no matches (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.keys.return_value = []

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test pattern invalidation with no matches
            result = cache.invalidate_pattern("nonexistent:*")

            assert result is True
            mock_redis_instance.keys.assert_called_once_with("nonexistent:*")
            mock_redis_instance.delete.assert_not_called()

    def test_cache_disabled_when_redis_unavailable(self):
        """Test cache service gracefully handles Redis unavailability (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client to fail
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.side_effect = redis.ConnectionError("Connection refused")

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Verify cache is disabled
            assert cache.enabled is False
            assert cache.redis_client is None

            # Test operations return appropriate values when disabled
            assert cache.get_cached("key") is None
            assert cache.cache_result("key", "value") is False
            assert cache.invalidate("key") is False
            assert cache.invalidate_pattern("pattern:*") is False

    def test_cache_error_handling_on_get(self):
        """Test cache handles errors during get operation (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.side_effect = redis.RedisError("Connection lost")

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test get operation with error
            result = cache.get_cached("test_key")

            assert result is None

    def test_cache_error_handling_on_set(self):
        """Test cache handles errors during set operation (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.setex.side_effect = redis.RedisError("Connection lost")

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test set operation with error
            result = cache.cache_result("test_key", {"data": "value"})

            assert result is False

    def test_cache_round_trip(self):
        """Test cache round-trip: set then get returns same value (14.1)"""
        with patch('redis.Redis') as mock_redis_class:
            # Setup mock Redis client
            mock_redis_instance = MagicMock()
            mock_redis_class.return_value = mock_redis_instance
            mock_redis_instance.ping.return_value = True

            # Store the serialized value for retrieval
            stored_value = None
            def mock_setex(key, ttl, value):
                nonlocal stored_value
                stored_value = value
                return True

            def mock_get(key):
                return stored_value

            mock_redis_instance.setex.side_effect = mock_setex
            mock_redis_instance.get.side_effect = mock_get

            # Import after mocking
            from services.cache_service import CacheService

            # Create cache service
            cache = CacheService()

            # Test round-trip
            original_data = {"user_id": 456, "score": 98, "achievements": ["first_submission", "perfect_score"]}
            cache.cache_result("test:roundtrip", original_data)
            retrieved_data = cache.get_cached("test:roundtrip")

            assert retrieved_data == original_data
