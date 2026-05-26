from __future__ import annotations
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from app.config import settings
from app.database import engine, Base, async_session_factory
from app.core.exceptions import AppException, RateLimitExceededException
from app.core.tags import tags_metadata
from app.middleware.logging import request_logging_middleware
from app.api.v1.auth import router as auth_router
from app.api.v1.api_keys import router as api_keys_router
from app.api.v1.bots import router as bots_router
from app.api.v1.messages import router as messages_router
from app.api.v1.subscriptions import router as subscriptions_router
from app.api.v1.usage import router as usage_router
from app.api.v1.webhooks import router as webhooks_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("telegram_notifier")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified")

    from app.services.subscription_service import seed_plans
    async with async_session_factory() as session:
        await seed_plans(session)
    logger.info("Subscription plans seeded")

    yield
    await engine.dispose()
    logger.info("Engine disposed")


app = FastAPI(
    title=settings.app_name,
    description="Multi-tenant REST API for sending Telegram notifications programmatically. "
    "Register bots, manage API keys, send messages, and track usage — all behind "
    "rate limits and subscription tiers.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "Telegram Notification API",
        "url": "https://github.com/gabrielevalvano/telegram-notification",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0",
    },
    servers=[
        {"url": os.environ.get("RENDER_EXTERNAL_URL", "http://localhost:8000"), "description": "API base URL"},
    ],
    openapi_tags=tags_metadata,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.middleware("http")(request_logging_middleware)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    headers = {}
    if isinstance(exc, RateLimitExceededException):
        headers["Retry-After"] = str(exc.retry_after)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=headers,
    )


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint. Returns the API status and version."""
    return {"status": "ok", "version": "1.0.0"}


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=app.openapi_tags,
        contact=app.contact,
        license_info=app.license_info,
        servers=app.servers,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerJWT": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT access token for user management endpoints. Obtain via `POST /auth/login`.",
        },
        "ApiKeyAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Key",
            "description": "API key for message sending. Create via `POST /api-keys`. Format: `sk_<base64>`.",
        },
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.include_router(auth_router, prefix="/api/v1")
app.include_router(api_keys_router, prefix="/api/v1")
app.include_router(bots_router, prefix="/api/v1")
app.include_router(messages_router, prefix="/api/v1")
app.include_router(subscriptions_router, prefix="/api/v1")
app.include_router(usage_router, prefix="/api/v1")
app.include_router(webhooks_router, prefix="/api/v1")
