from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class CreateWebhookRequest(BaseModel):
    bot_id: str = Field(description="ID of the bot to receive updates for")
    url: str = Field(description="HTTPS URL where Telegram events will be sent")
    events: list[str] | None = Field(None, description="Event types to subscribe to (e.g. `[\"message\"]`)")


class WebhookResponse(BaseModel):
    id: str = Field(description="Webhook ID (UUID)")
    bot_id: str = Field(description="Bot this webhook is attached to")
    url: str = Field(description="Webhook destination URL")
    events: list = Field(description="Subscribed event types")
    is_active: bool = Field(description="Whether the webhook is active")
    created_at: datetime = Field(description="Creation timestamp")

    model_config = {"from_attributes": True}
