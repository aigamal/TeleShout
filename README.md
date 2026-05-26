# TeleShout

Multi-tenant REST API for sending Telegram notifications programmatically. Built with FastAPI, PostgreSQL, and Redis — designed as a micro SaaS.

## Quick Start

```bash
cp .env.example .env
# Edit .env with your values (see Environment Variables below)
docker compose up -d
open http://localhost:8000/docs
```

## Environment Variables

Copy `.env.example` to `.env` and configure:

### Required

| Variable | Description | How to create |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+asyncpg://user:password@host:5432/dbname` — default works with docker compose |
| `SECRET_KEY` | Used to sign JWT tokens | Generate: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"` |
| `ENCRYPTION_KEY` | Used to encrypt bot tokens at rest (Fernet) | Generate: `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |

### Optional

| Variable | Default | Description |
|---|---|---|
| `ENVIRONMENT` | `development` | Set to `production` for production deployments |
| `DEBUG` | `true` | SQLAlchemy echo mode; set to `false` in production |
| `REDIS_URL` | *(empty)* | Redis connection string. **Optional** — falls back to in-memory rate limiter if unset or unreachable. <br>`redis://localhost:6379/0` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT access token lifetime in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | JWT refresh token lifetime in days |
| `CORS_ORIGINS` | `["*"]` | Allowed CORS origins as JSON array. Set to your frontend domain in production |
| `STRIPE_SECRET_KEY` | *(empty)* | Stripe secret key for subscription billing (Phase 2) |
| `STRIPE_WEBHOOK_SECRET` | *(empty)* | Stripe webhook signing secret (Phase 2) |
| `DEFAULT_MESSAGE_RATE_PER_MINUTE` | `5` | Default rate limit per minute for free-tier users |
| `DEFAULT_MESSAGE_RATE_PER_DAY` | `100` | Default rate limit per day for free-tier users |
| `DEFAULT_MAX_BOTS` | `1` | Default max bots for free-tier users |

### Production Checklist

```bash
# Generate strong secrets
python3 -c "import secrets; print(f'SECRET_KEY={secrets.token_urlsafe(32)}')"
python3 -c "from cryptography.fernet import Fernet; print(f'ENCRYPTION_KEY={Fernet.generate_key().decode()}')"

# Set these in your deployment environment (Railway/Render/AWS)
```

## API Endpoints

### Auth
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Create account |
| POST | `/api/v1/auth/login` | Login (returns JWT) |
| POST | `/api/v1/auth/refresh` | Refresh tokens |

### API Keys
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/api-keys` | Create (full key shown once) |
| GET | `/api/v1/api-keys` | List keys (prefixes only) |
| DELETE | `/api/v1/api-keys/{id}` | Revoke a key |

### Bots
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/bots` | Register a Telegram bot |
| GET | `/api/v1/bots` | List bots |
| GET | `/api/v1/bots/{id}` | Get bot details |
| PUT | `/api/v1/bots/{id}` | Update a bot |
| DELETE | `/api/v1/bots/{id}` | Delete a bot |

### Messages
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/messages/send` | Send a notification |

### Subscriptions
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/subscriptions/plans` | List plans |
| GET | `/api/v1/subscriptions/current` | Current subscription |

### Usage
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/usage` | Usage statistics |
| GET | `/api/v1/usage/current` | Current period usage |

### Webhooks
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/webhooks` | Create a webhook |
| GET | `/api/v1/webhooks` | List webhooks |
| DELETE | `/api/v1/webhooks/{id}` | Delete a webhook |

## Authentication

Two auth modes:
- **JWT** (Bearer token) — for management endpoints
- **API Key** (Bearer token, `sk_` prefix) — for sending messages

## Subscription Plans

| Plan | Price | Msgs/Day | Rate/Min | Bots |
|------|-------|----------|----------|------|
| Free | $0 | 100 | 5 | 1 |
| Starter | $9/mo | 5,000 | 50 | 3 |
| Pro | $29/mo | 25,000 | 300 | 10 |
| Enterprise | Custom | 1,000,000 | 10,000 | 100 |

## Tech Stack

- **FastAPI** — async Python web framework
- **PostgreSQL 16** — primary database
- **Redis 7** — rate limiting
- **SQLAlchemy 2.0** — async ORM
- **Alembic** — database migrations
- **Docker** — containerized deployment

## Deployment

Ready for Railway / Render. Set environment variables from `.env.example`.

## License

Apache 2.0
