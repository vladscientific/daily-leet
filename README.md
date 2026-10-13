# daily-leet

Sends one LeetCode problem on working days from a curated list in PostgreSQL to a Telegram chat. Weekends and public holidays for `COUNTRY` (via the `holidays` library) are skipped.

On process start it posts a Telegram status: `SEND_AT`, holiday country, whether Postgres connected, and how many problems / unsent rows there are. Cron then runs `python -m daily_leet send` every day at `SEND_AT`. That job sends the next URL, or “No more problems left to send.” if the queue is empty.

## Configuration

Set the following environment variables:

| Variable | Description |
| --- | --- |
| `DB_URL` | PostgreSQL connection string. |
| `BOT_ID` | Telegram bot token from [@BotFather](https://t.me/BotFather) (`<bot_id>:<secret>`). |
| `CHAT_ID` | Telegram chat id of the destination group (negative for groups/supergroups). |
| `SEND_AT` | Daily send time, ISO 8601 with timezone (`09:00:00+05:00` or `09:00:00Z`). |
| `COUNTRY` | ISO 3166-1 alpha-2 country code for the [`holidays`](https://pypi.org/project/holidays/) calendar (e.g. `US`, `RU`, `KZ`). |

Example:

```env
DB_URL=postgresql://USER:PASSWORD@HOST/dbname?sslmode=require&channel_binding=require
BOT_ID=123456789:AAExampleToken
CHAT_ID=-1001234567890
SEND_AT=09:00:00+05:00
COUNTRY=US
```

## Local run

Put the variables above in `.env` in the project root, then:

```bash
docker compose up --build -d
```

The container posts the startup Telegram message (params, DB status, next unsent URL), installs a crontab from `SEND_AT`, and runs `cron` for the daily send. Env vars come from `.env`.

```bash
docker compose down
```
