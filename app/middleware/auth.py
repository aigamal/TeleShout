from __future__ import annotations
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import decode_token, verify_api_key
from app.core.exceptions import UnauthorizedException
from app.models.user import User
from app.models.api_key import APIKey

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid Authorization header")

    token = auth_header.split(" ", 1)[1]

    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id or payload.get("type") not in ("access", "refresh"):
        raise UnauthorizedException("Invalid or expired token")

    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedException("User not found")

    return user


async def get_user_from_api_key(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise UnauthorizedException("Missing or invalid Authorization header")

    raw_key = auth_header.split(" ", 1)[1]

    result = await db.execute(select(APIKey).where(APIKey.is_active == True))
    all_keys = result.scalars().all()

    matched_key = None
    for api_key in all_keys:
        if verify_api_key(raw_key, api_key.key_hash):
            matched_key = api_key
            break

    if not matched_key:
        raise UnauthorizedException("Invalid API key")

    result = await db.execute(select(User).where(User.id == matched_key.user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedException("User not found")

    request.state.api_key_id = matched_key.id
    return user
