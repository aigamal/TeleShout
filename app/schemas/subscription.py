from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class SubscriptionPlanResponse(BaseModel):
    id: str = Field(description="Plan ID (UUID)")
    name: str = Field(description="Plan name (Free, Starter, Pro, Enterprise)")
    price_cents: int = Field(description="Price in cents (USD). 0 = free")
    currency: str = Field(description="ISO 4217 currency code")
    messages_per_day: int = Field(description="Max messages allowed per day")
    messages_per_minute: int = Field(description="Max messages allowed per minute")
    max_bots: int = Field(description="Max number of Telegram bots you can register")
    max_webhooks: int = Field(description="Max number of webhooks you can create")
    features: dict = Field(description="Feature flags for this plan")

    model_config = {"from_attributes": True}


class UserSubscriptionResponse(BaseModel):
    id: str = Field(description="Subscription ID (UUID)")
    plan: SubscriptionPlanResponse = Field(description="The subscribed plan details")
    status: str = Field(description="Subscription status: `active`, `cancelled`, `expired`, `trialing`")
    current_period_start: datetime | None = Field(None, description="Start of current billing period")
    current_period_end: datetime | None = Field(None, description="End of current billing period")
    created_at: datetime = Field(description="Subscription creation timestamp")

    model_config = {"from_attributes": True}
