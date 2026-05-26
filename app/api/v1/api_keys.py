from __future__ import annotations
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.api_key import APIKey
from app.core.security import generate_api_key
from app.core.exceptions import NotFoundException
from app.schemas.api_key import CreateAPIKeyRequest, CreateAPIKeyResponse, APIKeyResponse

router = APIRouter(prefix="/api-keys", tags=["API Keys"])


@router.post(
    "",
    response_model=CreateAPIKeyResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create an API key",
    description="Generate a new API key for programmatic access. The full key is returned **only once** "
    "in this response — save it securely. API keys are hashed with bcrypt before storage. "
    "They are used to authenticate message sending via the `Authorization: Bearer <key>` header.",
    response_description="API key details including the full raw key (shown once)",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
    },
)
async def create_api_key(
    body: CreateAPIKeyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    raw_key, prefix, key_hash = generate_api_key()
    api_key = APIKey(
        user_id=user.id,
        key_hash=key_hash,
        key_prefix=prefix,
        name=body.name,
    )
    db.add(api_key)
    await db.flush()

    return CreateAPIKeyResponse(
        id=api_key.id,
        key_prefix=prefix,
        raw_key=raw_key,
        name=body.name,
        created_at=api_key.created_at,
    )


@router.get(
    "",
    response_model=list[APIKeyResponse],
    summary="List API keys",
    description="List all API keys for the authenticated user. Only key prefixes are returned "
    "(first 10 characters). Full keys are never stored in plaintext.",
    response_description="List of API keys (prefixes only)",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
    },
)
async def list_api_keys(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(APIKey).where(APIKey.user_id == user.id).order_by(APIKey.created_at.desc())
    )
    return list(result.scalars().all())


@router.delete(
    "/{key_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke an API key",
    description="Permanently delete an API key. Once revoked, the key can no longer be used to send messages.",
    response_description="Key revoked successfully",
    responses={
        401: {"description": "Not authenticated (JWT required)"},
        404: {"description": "API key not found"},
    },
)
async def delete_api_key(
    key_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(APIKey).where(APIKey.id == key_id, APIKey.user_id == user.id)
    )
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise NotFoundException("API key not found")
    await db.delete(api_key)
