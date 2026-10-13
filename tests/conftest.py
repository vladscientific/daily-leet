from datetime import time, timezone

import pytest

from daily_leet.config import Config


@pytest.fixture
def config() -> Config:
    return Config(
        db_url="postgresql://user:pass@localhost/daily_leet",
        bot_id="123:token",
        chat_id="-1001",
        send_at=time(9, 0, 0, tzinfo=timezone.utc),
        country="US",
    )
