from __future__ import annotations
import time
import asyncio
import logging

logger = logging.getLogger("telegram_notifier")


class _InMemoryRateLimiter:
    """In-memory rate limiter used when Redis is unavailable."""

    def __init__(self):
        self._lock = asyncio.Lock()
        self._minute: dict[str, tuple[int, int]] = {}
        self._day: dict[str, tuple[int, int]] = {}

    async def check(
        self, user_id: str, max_per_minute: int, max_per_day: int
    ) -> tuple[bool, int, int, int]:
        now = int(time.time())
        minute_window = now // 60
        day_window = now // 86400

        async with self._lock:
            m_ts, m_count = self._minute.get(user_id, (minute_window, 0))
            if m_ts != minute_window:
                m_ts, m_count = minute_window, 0
            m_count += 1
            self._minute[user_id] = (m_ts, m_count)

            d_ts, d_count = self._day.get(user_id, (day_window, 0))
            if d_ts != day_window:
                d_ts, d_count = day_window, 0
            d_count += 1
            self._day[user_id] = (d_ts, d_count)

        minute_remaining = max(0, max_per_minute - m_count)
        day_remaining = max(0, max_per_day - d_count)
        retry_after = max(1, 60 - (now % 60))

        if m_count > max_per_minute:
            return False, retry_after, minute_remaining, day_remaining
        if d_count > max_per_day:
            return False, 0, minute_remaining, day_remaining
        return True, retry_after, minute_remaining, day_remaining


_redis_pool = None
_redis_attempted = False
_memory_limiter = _InMemoryRateLimiter()


async def _get_redis():
    global _redis_pool, _redis_attempted

    if _redis_attempted:
        return _redis_pool

    _redis_attempted = True
    from app.config import settings

    if not settings.redis_url:
        logger.info("No Redis URL configured — using in-memory rate limiter")
        return None

    try:
        import redis.asyncio as redis

        _redis_pool = redis.from_url(settings.redis_url, decode_responses=True)
        await _redis_pool.ping()
        logger.info("Connected to Redis for rate limiting")
        return _redis_pool
    except Exception as exc:
        logger.warning("Redis unavailable (%s) — falling back to in-memory rate limiter", exc)
        _redis_pool = None
        return None


async def check_rate_limit(
    user_id: str, max_per_minute: int, max_per_day: int
) -> tuple[bool, int, int, int]:
    r = await _get_redis()

    if r is None:
        return await _memory_limiter.check(user_id, max_per_minute, max_per_day)

    now = int(time.time())
    minute_key = f"rate:minute:{user_id}:{now // 60}"
    day_key = f"rate:day:{user_id}:{now // 86400}"

    minute_count = await r.incr(minute_key)
    if minute_count == 1:
        await r.expire(minute_key, 60)

    day_count = await r.incr(day_key)
    if day_count == 1:
        await r.expire(day_key, 86400)

    ttl_minute = await r.ttl(minute_key)
    if ttl_minute < 0:
        ttl_minute = 0

    remaining_minute = max(0, max_per_minute - minute_count)
    remaining_day = max(0, max_per_day - day_count)

    if minute_count > max_per_minute:
        return False, int(ttl_minute), remaining_minute, remaining_day
    if day_count > max_per_day:
        return False, 0, remaining_minute, remaining_day
    return True, int(ttl_minute), remaining_minute, remaining_day
