from __future__ import annotations
import time
import redis.asyncio as redis

from app.config import settings


_redis_pool = None


async def _get_redis():
    global _redis_pool
    if _redis_pool is None:
        _redis_pool = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_pool


async def check_rate_limit(user_id: str, max_per_minute: int, max_per_day: int) -> tuple[bool, int, int, int]:
    now = int(time.time())
    r = await _get_redis()

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
