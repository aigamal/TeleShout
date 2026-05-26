from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class UserResponse(BaseModel):
    id: str = Field(description="Unique user ID (UUID)")
    email: str = Field(description="User email address")
    full_name: str | None = Field(None, description="User display name")
    is_active: bool = Field(description="Whether the account is active")
    created_at: datetime = Field(description="Account creation timestamp")

    model_config = {"from_attributes": True}
