"""
Rate limiting middleware for the application.
"""
import time
from typing import Callable, Dict, Optional

from fastapi import Request, Response, status
from starlette.middleware.base import RequestResponseEndpoint
import redis

from app.core.config import settings


class RateLimitMiddleware:
    """
    Middleware for rate limiting API requests.
    Uses Redis to track request counts per client.
    """
    
    def __init__(self, rate_limit: int, time_window: int):
        """
        Initialize rate limiter.
        
        Args:
            rate_limit: Maximum number of requests allowed in time window
            time_window: Time window in seconds
        """
        self.rate_limit = rate_limit
        self.time_window = time_window
        self.redis_client: Optional[redis.Redis] = None
    
    def _get_redis_client(self) -> redis.Redis:
        """
        Get or create Redis client.
        
        Returns:
            redis.Redis: Redis client
        """
        if self.redis_client is None:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )
        return self.redis_client
    
    def _get_client_identifier(self, request: Request) -> str:
        """
        Get client identifier for rate limiting.
        
        Args:
            request: FastAPI request
            
        Returns:
            str: Client identifier (IP address or forwarded IP)
        """
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host
    
    async def __call__(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process request through rate limiter.
        
        Args:
            request: FastAPI request
            call_next: Next middleware or endpoint
            
        Returns:
            Response: FastAPI response
        """
        # Skip rate limiting for certain paths
        if request.url.path in ["/api/health", "/api/docs", "/api/redoc", "/api/openapi.json"]:
            return await call_next(request)
        
        client_id = self._get_client_identifier(request)
        redis_key = f"ratelimit:{client_id}"
        
        try:
            redis_client = self._get_redis_client()
            
            # Get current request count
            current_count = redis_client.get(redis_key)
            
            if current_count is None:
                # First request, set count to 1 with expiry
                redis_client.setex(redis_key, self.time_window, 1)
            elif int(current_count) >= self.rate_limit:
                # Rate limit exceeded
                return Response(
                    content='{"detail":"Rate limit exceeded"}',
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={"Retry-After": str(self.time_window)},
                )
            else:
                # Increment request count
                redis_client.incr(redis_key)
            
            # Add rate limit headers
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(self.rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(
                self.rate_limit - int(redis_client.get(redis_key) or 0)
            )
            response.headers["X-RateLimit-Reset"] = str(
                redis_client.ttl(redis_key)
            )
            
            return response
            
        except redis.RedisError:
            # If Redis is unavailable, continue without rate limiting
            return await call_next(request)