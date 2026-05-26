from __future__ import annotations
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import SubscriptionPlan, UserSubscription
from app.core.exceptions import NotFoundException


DEFAULT_PLANS = [
    {"name": "Free", "price_cents": 0, "messages_per_day": 100, "messages_per_minute": 5, "max_bots": 1, "max_webhooks": 0, "features": {"basic_support": True}},
    {"name": "Starter", "price_cents": 999, "messages_per_day": 5000, "messages_per_minute": 50, "max_bots": 3, "max_webhooks": 1, "features": {"priority_support": True, "analytics": True}},
    {"name": "Pro", "price_cents": 2999, "messages_per_day": 25000, "messages_per_minute": 300, "max_bots": 10, "max_webhooks": 5, "features": {"priority_support": True, "analytics": True, "webhooks": True}},
    {"name": "Enterprise", "price_cents": 0, "messages_per_day": 1000000, "messages_per_minute": 10000, "max_bots": 100, "max_webhooks": 50, "features": {"priority_support": True, "analytics": True, "webhooks": True, "sla": True}},
]


async def seed_plans(db: AsyncSession):
    for plan_data in DEFAULT_PLANS:
        result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.name == plan_data["name"]))
        existing = result.scalar_one_or_none()
        if not existing:
            plan = SubscriptionPlan(**plan_data)
            db.add(plan)
    await db.commit()


async def get_plans(db: AsyncSession) -> list[SubscriptionPlan]:
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.is_active == True).order_by(SubscriptionPlan.price_cents))
    return list(result.scalars().all())


async def get_plan_by_id(db: AsyncSession, plan_id: str) -> SubscriptionPlan:
    result = await db.execute(select(SubscriptionPlan).where(SubscriptionPlan.id == plan_id, SubscriptionPlan.is_active == True))
    plan = result.scalar_one_or_none()
    if not plan:
        raise NotFoundException("Plan not found")
    return plan


async def get_user_subscription(db: AsyncSession, user_id: str) -> UserSubscription | None:
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_limits_for_user(db: AsyncSession, user_id: str) -> tuple[int, int, int]:
    sub = await get_user_subscription(db, user_id)
    if sub and sub.plan:
        return sub.plan.messages_per_minute, sub.plan.messages_per_day, sub.plan.max_bots
    return 5, 100, 1
