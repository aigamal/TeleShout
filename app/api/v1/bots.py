from __future__ import annotations
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.bot import Bot
from app.models.subscription import UserSubscription
from app.core.security import encrypt_value
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.bot import CreateBotRequest, UpdateBotRequest, BotResponse

router = APIRouter(prefix="/bots", tags=["Bots"])


async def _get_max_bots(user_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    )
    sub = result.scalar_one_or_none()
    if sub and sub.plan:
        return sub.plan.max_bots
    return 1


@router.post(
    "",
    response_model=BotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a Telegram bot",
    description="Register a Telegram bot by providing its token (from BotFather) and a default chat ID. "
    "The token and chat ID are encrypted at rest using Fernet symmetric encryption. "
    "Your subscription tier limits how many bots you can register.",
    response_description="The registered bot (token and chat ID are never returned)",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
        403: {"description": "Bot limit reached for your plan"},
    },
)
async def create_bot(
    body: CreateBotRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    max_bots = await _get_max_bots(user.id, db)
    count_result = await db.execute(
        select(func.count(Bot.id)).where(Bot.user_id == user.id)
    )
    current_count = count_result.scalar() or 0

    if current_count >= max_bots:
        raise ForbiddenException(f"Max bots limit ({max_bots}) reached. Upgrade your plan.")

    bot = Bot(
        user_id=user.id,
        name=body.name,
        encrypted_token_id=encrypt_value(body.token_id),
        encrypted_chat_id=encrypt_value(body.chat_id),
    )
    db.add(bot)
    await db.flush()
    return BotResponse.model_validate(bot)


@router.get(
    "",
    response_model=list[BotResponse],
    summary="List bots",
    description="List all registered Telegram bots for the authenticated user. "
    "Bot tokens and chat IDs are never returned for security.",
    response_description="List of registered bots",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
    },
)
async def list_bots(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bot).where(Bot.user_id == user.id).order_by(Bot.created_at.desc())
    )
    return [BotResponse.model_validate(b) for b in result.scalars().all()]


@router.get(
    "/{bot_id}",
    response_model=BotResponse,
    summary="Get bot details",
    description="Get details of a specific registered bot.",
    response_description="Bot details (token and chat ID are never returned)",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
        404: {"description": "Bot not found"},
    },
)
async def get_bot(
    bot_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bot).where(Bot.id == bot_id, Bot.user_id == user.id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise NotFoundException("Bot not found")
    return BotResponse.model_validate(bot)


@router.put(
    "/{bot_id}",
    response_model=BotResponse,
    summary="Update a bot",
    description="Update a registered bot's name, token, or chat ID. "
    "Only provided fields are updated. New tokens/chat IDs are encrypted before storage.",
    response_description="The updated bot",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
        404: {"description": "Bot not found"},
    },
)
async def update_bot(
    bot_id: str,
    body: UpdateBotRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bot).where(Bot.id == bot_id, Bot.user_id == user.id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise NotFoundException("Bot not found")

    if body.name is not None:
        bot.name = body.name
    if body.token_id is not None:
        bot.encrypted_token_id = encrypt_value(body.token_id)
    if body.chat_id is not None:
        bot.encrypted_chat_id = encrypt_value(body.chat_id)

    await db.flush()
    return BotResponse.model_validate(bot)


@router.delete(
    "/{bot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a bot",
    description="Permanently delete a registered bot and all its associated messages and webhooks.",
    response_description="Bot deleted successfully",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
        404: {"description": "Bot not found"},
    },
)
async def delete_bot(
    bot_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bot).where(Bot.id == bot_id, Bot.user_id == user.id)
    )
    bot = result.scalar_one_or_none()
    if not bot:
        raise NotFoundException("Bot not found")
    await db.delete(bot)
