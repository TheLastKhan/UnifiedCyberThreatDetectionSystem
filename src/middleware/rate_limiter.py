"""
Rate limiting middleware using Redis
Prevents API abuse and enforces usage quotas
"""

import os
import time
from functools import wraps
from flask import request, jsonify
from typing import Optional, Tuple
import logging

from src.utils.cache import get_redis_cache

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter using Redis
    """
    
    def __init__(self, 
                 requests_per_minute: int = 60,
                 requests_per_hour: int = 1000,
                 requests_per_day: int = 10000):
        """
        Initialize rate limiter
        
        Args:
            requests_per_minute: Max requests per minute per IP
            requests_per_hour: Max requests per hour per IP
            requests_per_day: Max requests per day per IP
        """
        self.rpm = int(os.getenv('RATE_LIMIT_PER_MINUTE', requests_per_minute))
        self.rph = int(os.getenv('RATE_LIMIT_PER_HOUR', requests_per_hour))
        self.rpd = int(os.getenv('RATE_LIMIT_PER_DAY', requests_per_day))
        
        self.cache = get_redis_cache()
        self.enabled = self.cache.enabled
        
        if not self.enabled:
            logger.warning("Rate limiting disabled (Redis not available)")
    
    def _get_identifier(self) -> str:
        """
        Get unique identifier for rate limiting (IP address)
        
        Returns:
            str: Client IP address
        """
        # Try to get real IP behind proxy
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()  # type: ignore[union-attr]
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')  # type: ignore[return-value]
        else:
            return request.remote_addr or 'unknown'
    
    def _check_limit(self, key: str, limit: int, window: int) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit
        
        Args:
            key: Redis key for this limit
            limit: Max requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (allowed: bool, current_count: int, retry_after: int)
        """
        try:
            current = self.cache.client.get(key)  # type: ignore[union-attr]
            
            if current is None:
                # First request in window
                self.cache.client.setex(key, window, 1)  # type: ignore[union-attr]
                return True, 1, 0
            
            current = int(current)
            
            if current < limit:
                # Within limit, increment counter
                self.cache.client.incr(key)  # type: ignore[union-attr]
                return True, current + 1, 0
            else:
                # Rate limit exceeded
                ttl = self.cache.client.ttl(key)  # type: ignore[union-attr]
                return False, current, ttl if ttl > 0 else window
                
        except Exception as e:
            logger.error(f"Rate limit check error: {e}")
            # On error, allow request (fail open)
            return True, 0, 0
    
    def check_rate_limit(self) -> Optional[dict]:
        """
        Check all rate limits for current request
        
        Returns:
            dict: Error response if rate limited, None if allowed
        """
        if not self.enabled:
            return None
        
        identifier = self._get_identifier()
        timestamp = int(time.time())
        
        # Check minute limit
        minute_key = f"ratelimit:{identifier}:minute:{timestamp // 60}"
        minute_ok, minute_count, minute_retry = self._check_limit(minute_key, self.rpm, 60)
        
        if not minute_ok:
            return {
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Limit: {self.rpm} requests/minute',
                'retry_after': minute_retry,
                'limit_type': 'minute',
                'current_usage': minute_count,
                'limit': self.rpm
            }
        
        # Check hour limit
        hour_key = f"ratelimit:{identifier}:hour:{timestamp // 3600}"
        hour_ok, hour_count, hour_retry = self._check_limit(hour_key, self.rph, 3600)
        
        if not hour_ok:
            return {
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Limit: {self.rph} requests/hour',
                'retry_after': hour_retry,
                'limit_type': 'hour',
                'current_usage': hour_count,
                'limit': self.rph
            }
        
        # Check day limit
        day_key = f"ratelimit:{identifier}:day:{timestamp // 86400}"
        day_ok, day_count, day_retry = self._check_limit(day_key, self.rpd, 86400)
        
        if not day_ok:
            return {
                'error': 'Rate limit exceeded',
                'message': f'Too many requests. Limit: {self.rpd} requests/day',
                'retry_after': day_retry,
                'limit_type': 'day',
                'current_usage': day_count,
                'limit': self.rpd
            }
        
        # All checks passed
        return None
    
    def get_usage_info(self) -> dict:
        """
        Get current rate limit usage for client
        
        Returns:
            dict: Usage statistics
        """
        if not self.enabled:
            return {'enabled': False}
        
        identifier = self._get_identifier()
        timestamp = int(time.time())
        
        minute_key = f"ratelimit:{identifier}:minute:{timestamp // 60}"
        hour_key = f"ratelimit:{identifier}:hour:{timestamp // 3600}"
        day_key = f"ratelimit:{identifier}:day:{timestamp // 86400}"
        
        try:
            minute_count = int(self.cache.client.get(minute_key) or 0)  # type: ignore[union-attr]
            hour_count = int(self.cache.client.get(hour_key) or 0)  # type: ignore[union-attr]
            day_count = int(self.cache.client.get(day_key) or 0)  # type: ignore[union-attr]
            
            return {
                'enabled': True,
                'identifier': identifier,
                'limits': {
                    'per_minute': self.rpm,
                    'per_hour': self.rph,
                    'per_day': self.rpd
                },
                'usage': {
                    'minute': minute_count,
                    'hour': hour_count,
                    'day': day_count
                },
                'remaining': {
                    'minute': max(0, self.rpm - minute_count),
                    'hour': max(0, self.rph - hour_count),
                    'day': max(0, self.rpd - day_count)
                }
            }
        except Exception as e:
            logger.error(f"Error getting usage info: {e}")
            return {'enabled': True, 'error': str(e)}


def rate_limit(requests_per_minute: Optional[int] = None,
               requests_per_hour: Optional[int] = None,
               requests_per_day: Optional[int] = None):
    """
    Decorator for rate limiting Flask routes
    
    Args:
        requests_per_minute: Override default RPM
        requests_per_hour: Override default RPH
        requests_per_day: Override default RPD
        
    Usage:
        @app.route('/api/analyze')
        @rate_limit(requests_per_minute=10)
        def analyze():
            return {"result": "..."}
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create rate limiter with custom limits if provided
            limiter = RateLimiter(
                requests_per_minute=requests_per_minute or 60,
                requests_per_hour=requests_per_hour or 1000,
                requests_per_day=requests_per_day or 10000
            )
            
            # Check rate limit
            error_response = limiter.check_rate_limit()
            
            if error_response:
                return jsonify(error_response), 429
            
            # Execute function
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global singleton instance
_rate_limiter = None

def get_rate_limiter() -> RateLimiter:
    """Get or create rate limiter singleton"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
