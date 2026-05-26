from __future__ import annotations
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.usage_log import UsageLog
from app.models.message import Message


async def log_usage(db: AsyncSession, user_id: str, endpoint: str, status_code: int, response_time_ms: int | None = None, api_key_id: str | None = None):
    log = UsageLog(
        user_id=user_id,
        api_key_id=api_key_id,
        endpoint=endpoint,
        status_code=status_code,
        response_time_ms=response_time_ms,
    )
    db.add(log)


async def get_usage_stats(db: AsyncSession, user_id: str, days: int = 30) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    msg_count = await db.scalar(
        select(func.count(Message.id)).where(
            Message.user_id == user_id,
            Message.created_at >= since,
        )
    )

    api_count = await db.scalar(
        select(func.count(UsageLog.id)).where(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= since,
        )
    )

    return {
        "total_messages": msg_count or 0,
        "total_api_calls": api_count or 0,
        "period_days": days,
    }


async def get_current_usage(db: AsyncSession, user_id: str) -> dict:
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    msg_count = await db.scalar(
        select(func.count(Message.id)).where(
            Message.user_id == user_id,
            Message.created_at >= today_start,
        )
    )

    api_count = await db.scalar(
        select(func.count(UsageLog.id)).where(
            UsageLog.user_id == user_id,
            UsageLog.created_at >= today_start,
        )
    )

    return {
        "messages_sent_today": msg_count or 0,
        "api_calls_today": api_count or 0,
    }
