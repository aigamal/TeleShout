from __future__ import annotations
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, RefreshRequest
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Returns JWT access and refresh tokens. "
    "The email must be unique.",
    response_description="JWT tokens for the newly created account",
    responses={
        409: {"description": "Email already registered"},
        422: {"description": "Validation error (invalid email, weak password)"},
    },
)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.register_user(db, body.email, body.password, body.full_name)
    return await auth_service.create_tokens(user)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description="Authenticate with email and password. Returns JWT access and refresh tokens.",
    response_description="JWT tokens for the authenticated session",
    responses={
        401: {"description": "Invalid email or password"},
    },
)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await auth_service.authenticate_user(db, body.email, body.password)
    return await auth_service.create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token and refresh token pair. "
    "Refresh tokens expire after 7 days.",
    response_description="New JWT token pair",
    responses={
        401: {"description": "Invalid or expired refresh token"},
    },
)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await auth_service.refresh_access_token(db, body.refresh_token)
