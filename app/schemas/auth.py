from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    email: EmailStr = Field(description="Email address for the account")
    password: str = Field(description="Password (min 8 characters)")
    full_name: str | None = Field(None, description="Optional display name")


class LoginRequest(BaseModel):
    email: EmailStr = Field(description="Registered email address")
    password: str = Field(description="Account password")


class TokenResponse(BaseModel):
    access_token: str = Field(description="JWT access token (expires in 30 minutes)")
    refresh_token: str = Field(description="JWT refresh token (expires in 7 days)")
    token_type: str = Field("bearer", description="Token type")


class RefreshRequest(BaseModel):
    refresh_token: str = Field(description="Valid refresh token to exchange for new tokens")
