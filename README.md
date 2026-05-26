# TeleShout

Multi-tenant REST API for sending Telegram notifications programmatically. Built with FastAPI, PostgreSQL, and Redis — designed as a micro SaaS.

## Quick Start

```bash
cp .env.example .env
docker compose up -d
open http://localhost:8000/docs
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
