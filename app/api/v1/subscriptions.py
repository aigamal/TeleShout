from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.schemas.subscription import SubscriptionPlanResponse, UserSubscriptionResponse
from app.services import subscription_service

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.get(
    "/plans",
    response_model=list[SubscriptionPlanResponse],
    summary="List subscription plans",
    description="Get all available subscription plans with their limits and pricing. "
    "Plans control rate limits, max bots, and feature access. No authentication required.",
    response_description="List of available subscription plans",
)
async def list_plans(db: AsyncSession = Depends(get_db)):
    plans = await subscription_service.get_plans(db)
    return [SubscriptionPlanResponse.model_validate(p) for p in plans]


@router.get(
    "/current",
    response_model=Optional[UserSubscriptionResponse],
    summary="Get current subscription",
    description="Get the authenticated user's current subscription details, "
    "including the plan, status, and billing period. Returns null if no subscription exists "
    "(user is on the default Free plan).",
    response_description="Current subscription details or null",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
    },
)
async def current_subscription(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await subscription_service.get_user_subscription(db, user.id)
    if not sub:
        return None
    return UserSubscriptionResponse.model_validate(sub)
