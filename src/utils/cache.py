"""
Redis caching utilities for API performance optimization
"""

import os
import json
import redis  # type: ignore[import]
from typing import Optional, Any
from functools import wraps
import hashlib
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """
    Redis cache manager with automatic serialization/deserialization
    """
    
    client: Optional[redis.Redis]
    enabled: bool
    host: str
    port: int
    password: Optional[str]
    db: int
    
    def __init__(self, 
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 db: int = 0,
                 password: Optional[str] = None,
                 decode_responses: bool = True):
        """
        Initialize Redis connection
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (if authentication enabled)
            decode_responses: Auto-decode bytes to strings
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = int(port or os.getenv('REDIS_PORT', '6379'))
        self.password = password or os.getenv('REDIS_PASSWORD')
        self.db = db
        
        try:
            self.client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=decode_responses,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.client.ping()  # type: ignore[union-attr]
            self.enabled = True
            logger.info(f"Redis cache connected: {self.host}:{self.port}")
            
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"Redis connection failed: {e}. Cache disabled.")
            self.enabled = False
            self.client = None
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)  # type: ignore[union-attr]
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds (default: 1 hour)
            
        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value)
            self.client.setex(key, ttl, serialized)  # type: ignore[union-attr]
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from cache
        
        Args:
            key: Cache key
            
        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False
        
        try:
            self.client.delete(key)  # type: ignore[union-attr]
            return True
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if key exists
        """
        if not self.enabled:
            return False
        
        try:
            return bool(self.client.exists(key))  # type: ignore[union-attr]
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {e}")
            return False
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """
        Increment counter
        
        Args:
            key: Cache key
            amount: Increment amount
            
        Returns:
            New counter value or None
        """
        if not self.enabled:
            return None
        
        try:
            return self.client.incrby(key, amount)  # type: ignore[union-attr]
        except Exception as e:
            logger.error(f"Redis INCRBY error for key {key}: {e}")
            return None
    
    def expire(self, key: str, ttl: int) -> bool:
        """
        Set expiration on existing key
        
        Args:
            key: Cache key
            ttl: Time to live in seconds
            
        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False
        
        try:
            self.client.expire(key, ttl)  # type: ignore[union-attr]
            return True
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {e}")
            return False
    
    def flush_all(self) -> bool:
        """
        Clear all cache (use with caution!)
        
        Returns:
            bool: Success status
        """
        if not self.enabled:
            return False
        
        try:
            self.client.flushdb()  # type: ignore[union-attr]
            logger.warning("Redis cache flushed!")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False


def cache_key(*args, **kwargs) -> str:
    """
    Generate consistent cache key from function arguments
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        str: MD5 hash of arguments
    """
    key_data = str(args) + str(sorted(kwargs.items()))
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 3600, key_prefix: str = ''):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache keys
        
    Usage:
        @cached(ttl=300, key_prefix='email_analysis')
        def analyze_email(email_content):
            # expensive operation
            return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_redis_cache()
            
            if not cache.enabled:
                # Cache disabled, execute function normally
                return func(*args, **kwargs)
            
            # Generate cache key
            key_suffix = cache_key(*args, **kwargs)
            full_key = f"{key_prefix}:{func.__name__}:{key_suffix}"
            
            # Try to get from cache
            cached_result = cache.get(full_key)
            if cached_result is not None:
                logger.debug(f"Cache HIT: {full_key}")
                return cached_result
            
            # Cache miss, execute function
            logger.debug(f"Cache MISS: {full_key}")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(full_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global singleton instance
_redis_cache = None

def get_redis_cache() -> RedisCache:
    """Get or create Redis cache singleton"""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache
