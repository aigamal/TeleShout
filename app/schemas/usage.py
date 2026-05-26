from __future__ import annotations
from pydantic import BaseModel, Field


class UsageStatsResponse(BaseModel):
    total_messages: int = Field(description="Total messages sent in the period")
    total_api_calls: int = Field(description="Total API calls made in the period")
    period_days: int = Field(description="Number of days in the reporting period")


class CurrentUsageResponse(BaseModel):
    messages_sent_today: int = Field(description="Messages sent today (UTC)")
    messages_limit_per_day: int = Field(description="Daily message limit based on plan")
    api_calls_today: int = Field(description="API calls made today (UTC)")
    period_reset: str | None = Field(None, description="When the current period resets")
