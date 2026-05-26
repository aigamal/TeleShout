from __future__ import annotations
from fastapi import APIRouter, Depends, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.bot import Bot
from app.models.webhook import Webhook
from app.models.subscription import UserSubscription
from app.core.exceptions import NotFoundException, ForbiddenException
from app.schemas.webhook import CreateWebhookRequest, WebhookResponse

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


async def _get_max_webhooks(user_id: str, db: AsyncSession) -> int:
    result = await db.execute(
        select(UserSubscription).where(UserSubscription.user_id == user_id)
    )
    sub = result.scalar_one_or_none()
    if sub and sub.plan:
        return sub.plan.max_webhooks
    return 0


@router.post(
    "",
    response_model=WebhookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a webhook",
    description="Register a webhook URL to receive real-time Telegram events for a bot. "
    "When events occur, Telegram will POST updates to your URL. "
    "Your subscription tier limits how many webhooks you can create.",
    response_description="The created webhook",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
        403: {"description": "Webhook limit reached for your plan"},
        404: {"description": "Bot not found"},
    },
)
async def create_webhook(
    body: CreateWebhookRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    bot_result = await db.execute(
        select(Bot).where(Bot.id == body.bot_id, Bot.user_id == user.id)
    )
    bot = bot_result.scalar_one_or_none()
    if not bot:
        raise NotFoundException("Bot not found")

    max_webhooks = await _get_max_webhooks(user.id, db)
    count_result = await db.execute(
        select(func.count(Webhook.id)).where(Webhook.user_id == user.id)
    )
    current_count = count_result.scalar() or 0

    if current_count >= max_webhooks:
        raise ForbiddenException(f"Max webhooks limit ({max_webhooks}) reached. Upgrade your plan.")

    webhook = Webhook(
        user_id=user.id,
        bot_id=body.bot_id,
        url=body.url,
        events=body.events or ["message"],
    )
    db.add(webhook)
    await db.flush()
    return WebhookResponse.model_validate(webhook)


@router.get(
    "",
    response_model=list[WebhookResponse],
    summary="List webhooks",
    description="List all registered webhooks for the authenticated user.",
    response_description="List of registered webhooks",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
    },
)
async def list_webhooks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Webhook).where(Webhook.user_id == user.id).order_by(Webhook.created_at.desc())
    )
    return [WebhookResponse.model_validate(w) for w in result.scalars().all()]


@router.delete(
    "/{webhook_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a webhook",
    description="Permanently remove a webhook. Telegram will stop sending updates to the registered URL.",
    response_description="Webhook deleted successfully",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
        404: {"description": "Webhook not found"},
    },
)
async def delete_webhook(
    webhook_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Webhook).where(Webhook.id == webhook_id, Webhook.user_id == user.id)
    )
    webhook = result.scalar_one_or_none()
    if not webhook:
        raise NotFoundException("Webhook not found")
    await db.delete(webhook)
