from __future__ import annotations
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_user_from_api_key
from app.models.user import User
from app.models.bot import Bot
from app.models.message import Message
from app.core.exceptions import NotFoundException, AppException
from app.schemas.message import SendMessageRequest, MessageResponse
from app.services.telegram_service import send_notification
from app.services.usage_service import log_usage

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.post(
    "/send",
    response_model=MessageResponse,
    summary="Send a Telegram notification",
    description="Send a message via a registered Telegram bot. "
    "Authenticate with an **API key** (not JWT) in the `Authorization: Bearer <key>` header. "
    "The message supports HTML formatting by default. "
    "Delivery status (`sent` or `failed`) is recorded and returned. "
    "This endpoint is subject to rate limiting based on your subscription plan.",
    response_description="Message delivery result with status and details",
    responses={
        401: {"description": "Invalid or missing API key"},
        404: {"description": "Bot not found or not active"},
        429: {"description": "Rate limit exceeded (check Retry-After header)"},
        502: {"description": "Telegram API returned an error"},
    },
)
async def send_message(
    body: SendMessageRequest,
    request: Request,
    user: User = Depends(get_user_from_api_key),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bot).where(Bot.id == body.bot_id, Bot.user_id == user.id, Bot.is_active == True)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise NotFoundException("Bot not found or not active")

    chat_id = body.chat_id or decrypt_value_if_needed(bot.encrypted_chat_id)
    if not chat_id:
        raise AppException("No chat_id provided and bot has no default chat_id")

    try:
        telegram_response = await send_notification(
            bot.encrypted_token_id,
            bot.encrypted_chat_id,
            body.message,
            body.parse_mode or "HTML",
        )
        telegram_message_id = str(telegram_response.get("result", {}).get("message_id", ""))
        status_result = "sent"
        error = None
    except Exception as e:
        telegram_message_id = ""
        status_result = "failed"
        error = str(e)

    msg = Message(
        user_id=user.id,
        bot_id=bot.id,
        chat_id=chat_id,
        text=body.message,
        parse_mode=body.parse_mode,
        status=status_result,
        error_message=error,
        telegram_message_id=telegram_message_id,
    )
    db.add(msg)
    await db.flush()

    api_key_id = getattr(request.state, "api_key_id", None)
    await log_usage(db, user.id, "POST /messages/send", 200 if status_result == "sent" else 500, api_key_id=api_key_id)

    return MessageResponse.model_validate(msg)


def decrypt_value_if_needed(encrypted_value: str) -> str:
    from app.core.security import decrypt_value
    try:
        return decrypt_value(encrypted_value)
    except Exception:
        return encrypted_value
