from __future__ import annotations
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import get_db


@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_register(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/auth/register",
            json={"email": "test@example.com", "password": "StrongPass1!"},
        )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/api/v1/auth/register",
            json={"email": "login@test.com", "password": "StrongPass1!"},
        )
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "login@test.com", "password": "StrongPass1!"},
        )
    assert response.status_code == 200
    assert "access_token" in response.json()

    app.dependency_overrides.clear()
