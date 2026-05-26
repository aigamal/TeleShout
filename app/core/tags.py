from __future__ import annotations


tags_metadata = [
    {
        "name": "Auth",
        "description": "User registration, login, and token refresh. These endpoints use **JWT** authentication for user session management.",
    },
    {
        "name": "API Keys",
        "description": "Create and manage API keys for programmatic access. API keys use the format `sk_<base64>` and are hashed with bcrypt before storage. **Full key is shown only once at creation.**",
    },
    {
        "name": "Bots",
        "description": "Register and manage Telegram bots. Each bot stores a Telegram bot token and chat ID, both encrypted at rest using Fernet symmetric encryption. Bot limits depend on your subscription tier.",
    },
    {
        "name": "Messages",
        "description": "Send Telegram notifications. This is the core endpoint — authenticated via **API key** (not JWT). Messages are sent to the Telegram API and delivery status is recorded.",
    },
    {
        "name": "Subscriptions",
        "description": "View available subscription plans and your current subscription. Subscription plans control rate limits, max bots, and feature access.",
    },
    {
        "name": "Usage",
        "description": "View API usage statistics. Track messages sent, API calls made, and compare against your plan limits.",
    },
    {
        "name": "Webhooks",
        "description": "Register webhooks to receive real-time Telegram updates. Webhooks forward Telegram events to your specified URL.",
    },
]
