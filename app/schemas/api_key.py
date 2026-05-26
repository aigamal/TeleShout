from __future__ import annotations
from pydantic import BaseModel, Field
from datetime import datetime


class CreateAPIKeyRequest(BaseModel):
    name: str | None = Field(None, description="Optional label to identify this key")


class CreateAPIKeyResponse(BaseModel):
    id: str = Field(description="API key ID (UUID)")
    key_prefix: str = Field(description="First 10 characters of the raw key for identification")
    raw_key: str = Field(description="The full API key. **Save this — it will not be shown again.** Format: `sk_<base64>`")
    name: str | None = Field(None, description="Key label")
    created_at: datetime = Field(description="Creation timestamp")


class APIKeyResponse(BaseModel):
    id: str = Field(description="API key ID (UUID)")
    key_prefix: str = Field(description="First 10 characters of the key")
    name: str | None = Field(None, description="Key label")
    is_active: bool = Field(description="Whether the key is active")
    last_used_at: datetime | None = Field(None, description="Timestamp of last use")
    created_at: datetime = Field(description="Creation timestamp")

    model_config = {"from_attributes": True}
