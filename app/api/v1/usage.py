from __future__ import annotations
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.usage import UsageStatsResponse, CurrentUsageResponse
from app.services import usage_service, subscription_service

router = APIRouter(prefix="/usage", tags=["Usage"])


@router.get(
    "",
    response_model=UsageStatsResponse,
    summary="Get usage statistics",
    description="Get historical usage statistics for the authenticated user. "
    "Returns total messages sent and API calls made over the specified period.",
    response_description="Usage statistics for the period",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
    },
)
async def get_usage(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back (1-365)"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stats = await usage_service.get_usage_stats(db, user.id, days)
    return UsageStatsResponse(**stats)


@router.get(
    "/current",
    response_model=CurrentUsageResponse,
    summary="Get current period usage",
    description="Get the authenticated user's current billing period usage. "
    "Shows today's message count and API calls alongside the plan limits.",
    response_description="Current usage vs plan limits",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
    },
)
async def get_current_usage(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    limits = await subscription_service.get_limits_for_user(db, user.id)
    usage = await usage_service.get_current_usage(db, user.id)
    return CurrentUsageResponse(
        messages_sent_today=usage["messages_sent_today"],
        messages_limit_per_day=limits[1],
        api_calls_today=usage["api_calls_today"],
        period_reset="midnight UTC",
    )
