from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class SendMessageRequest(BaseModel):
    bot_id: str = Field(description="ID of the registered bot to send from")
    chat_id: str | None = Field(None, description="Override chat ID. Uses bot's default if not provided.")
    message: str = Field(description="Message text to send. Supports HTML formatting.")
    parse_mode: str | None = Field("HTML", description="Telegram parse mode: `HTML` or `Markdown`")


class MessageResponse(BaseModel):
    id: str = Field(description="Message ID (UUID)")
    bot_id: str = Field(description="Bot used to send")
    chat_id: str = Field(description="Recipient chat ID")
    text: str = Field(description="Message content sent")
    status: str = Field(description="Delivery status: `sent` or `failed`")
    error_message: str | None = Field(None, description="Error details if delivery failed")
    created_at: datetime = Field(description="Send timestamp")

    model_config = {"from_attributes": True}
