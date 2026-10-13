import json

import httpx
import pytest

from daily_leet.telegram import TelegramError, send_message


def _handler(ok: bool, status: int = 200):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/sendMessage")
        body = json.loads(request.content)
        assert body["chat_id"] == "-1001"
        assert body["text"] == "https://leetcode.com/problems/two-sum/"
        if ok:
            return httpx.Response(status, json={"ok": True, "result": {}})
        return httpx.Response(status, json={"ok": False, "description": "Forbidden"})

    return handler


def test_send_message_ok():
    transport = httpx.MockTransport(_handler(ok=True))
    with httpx.Client(transport=transport) as client:
        send_message("123:token", "-1001", "https://leetcode.com/problems/two-sum/", client=client)


def test_send_message_api_error():
    transport = httpx.MockTransport(_handler(ok=False))
    with httpx.Client(transport=transport) as client:
        with pytest.raises(TelegramError, match="Forbidden"):
            send_message("123:token", "-1001", "https://leetcode.com/problems/two-sum/", client=client)
