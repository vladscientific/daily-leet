from __future__ import annotations

import httpx

TELEGRAM_API = "https://api.telegram.org"


class TelegramError(Exception):
    pass


def send_message(
    bot_id: str,
    chat_id: str,
    text: str,
    *,
    client: httpx.Client | None = None,
) -> None:
    url = f"{TELEGRAM_API}/bot{bot_id}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if client is None:
        with httpx.Client(timeout=30.0) as owned:
            _post(owned, url, payload)
        return
    _post(client, url, payload)


def _post(client: httpx.Client, url: str, payload: dict[str, str]) -> None:
    try:
        response = client.post(url, json=payload)
        response.raise_for_status()
        body = response.json()
    except httpx.HTTPError as exc:
        raise TelegramError(f"Telegram request failed: {exc}") from exc

    if not body.get("ok"):
        description = body.get("description", "unknown error")
        raise TelegramError(f"Telegram API error: {description}")
