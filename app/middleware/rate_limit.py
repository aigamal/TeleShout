from __future__ import annotations
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.exceptions import RateLimitExceededException
from app.services.rate_limiter import check_rate_limit


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        if not hasattr(request.state, "user_id"):
            return await call_next(request)

        if not hasattr(request.state, "rate_limits"):
            return await call_next(request)

        limits = request.state.rate_limits
        max_per_minute = limits.get("max_per_minute", 5)
        max_per_day = limits.get("max_per_day", 100)

        allowed, retry_after, remaining_min, remaining_day = await check_rate_limit(
            request.state.user_id, max_per_minute, max_per_day
        )

        if not allowed:
            raise RateLimitExceededException(retry_after=retry_after)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit-Minute"] = str(max_per_minute)
        response.headers["X-RateLimit-Limit-Day"] = str(max_per_day)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining_min)
        response.headers["X-RateLimit-Remaining-Day"] = str(remaining_day)

        return response
