from __future__ import annotations
from fastapi import Request

from app.models.user import User
from app.middleware.auth import get_current_user, get_user_from_api_key
from app.services.subscription_service import get_limits_for_user
from app.database import get_db


async def get_current_user_with_limits(request: Request) -> User:
    db_gen = get_db()
    db = await db_gen.__anext__()
    try:
        auth_type = request.headers.get("X-Auth-Type", "jwt")
        if auth_type == "api_key":
            user = await get_user_from_api_key(request, db)
        else:
            user = await get_current_user(request, db)

        limits = await get_limits_for_user(db, user.id)
        request.state.user_id = user.id
        request.state.rate_limits = {
            "max_per_minute": limits[0],
            "max_per_day": limits[1],
            "max_bots": limits[2],
        }
        return user
    finally:
        await db.close()
