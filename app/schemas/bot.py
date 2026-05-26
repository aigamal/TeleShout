from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class CreateBotRequest(BaseModel):
    name: str = Field(description="A friendly name for this bot")
    token_id: str = Field(description="Telegram bot token from BotFather (e.g. `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)")
    chat_id: str = Field(description="Default Telegram chat ID or @username to send messages to")


class UpdateBotRequest(BaseModel):
    name: str | None = Field(None, description="New name for the bot")
    token_id: str | None = Field(None, description="New Telegram bot token")
    chat_id: str | None = Field(None, description="New default chat ID")


class BotResponse(BaseModel):
    id: str = Field(description="Bot ID (UUID)")
    name: str = Field(description="Bot name")
    is_active: bool = Field(description="Whether the bot is active")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")

    model_config = {"from_attributes": True}
