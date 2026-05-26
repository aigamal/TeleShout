from __future__ import annotations
import pytest


@pytest.mark.asyncio
async def test_send_message_no_auth():
    from httpx import AsyncClient, ASGITransport
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/messages/send",
            json={"bot_id": "test", "message": "Hello"},
        )
    assert response.status_code == 401
