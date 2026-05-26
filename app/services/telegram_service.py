from __future__ import annotations
import httpx

from app.core.security import decrypt_value
from app.core.exceptions import AppException


async def send_telegram_message(token_id: str, chat_id: str, text: str, parse_mode: str = "HTML") -> dict:
    url = f"https://api.telegram.org/bot{token_id}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, data=payload)
        data = response.json()

    if not data.get("ok"):
        error_desc = data.get("description", "Unknown error")
        raise AppException(f"Telegram API error: {error_desc}")

    return data


async def send_notification(encrypted_token_id: str, encrypted_chat_id: str, message: str, parse_mode: str = "HTML") -> dict:
    token_id = decrypt_value(encrypted_token_id)
    chat_id = decrypt_value(encrypted_chat_id)
    return await send_telegram_message(token_id, chat_id, message, parse_mode)
