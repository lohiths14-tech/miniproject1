"""
Redis caching service for performance optimization
"""
import redis
import json
from functools import wraps
from config import Config


class CacheService:
    """Redis-based caching service"""

    def __init__(self):
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST if hasattr(Config, 'REDIS_HOST') else 'localhost',
                port=Config.REDIS_PORT if hasattr(Config, 'REDIS_PORT') else 6379,
                db=0,
                decode_responses=True
            )
            self.redis_client.ping()
            self.enabled = True
        except Exception as e:
            print(f"Redis not available: {e}. Caching disabled.")
            self.enabled = False
            self.redis_client = None

    def cache_result(self, key, value, expiration=3600):
        """Cache a result with expiration time"""
        if not self.enabled:
            return False

        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, expiration, serialized)
            return True
        except Exception as e:
            print(f"Cache set error: {e}")
            return False

    def get_cached(self, key):
        """Retrieve cached result"""
        if not self.enabled:
            return None

        try:
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None

    def invalidate(self, key):
        """Invalidate a cache key"""
        if not self.enabled:
            return False

        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False

    def invalidate_pattern(self, pattern):
        """Invalidate all keys matching pattern"""
        if not self.enabled:
            return False

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception as e:
            print(f"Cache pattern delete error: {e}")
            return False


# Decorator for caching function results
def cached(expiration=3600, key_prefix=''):
    """
    Decorator to cache function results

    Usage:
        @cached(expiration=1800, key_prefix='user')
        def get_user_profile(user_id):
            return expensive_operation(user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = cache_service

            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{args}:{kwargs}"

            # Try to get from cache
            cached_result = cache.get_cached(cache_key)
            if cached_result is not None:
                return cached_result

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.cache_result(cache_key, result, expiration)

            return result
        return wrapper
    return decorator


# Global cache service instance
cache_service = CacheService()
