#!/bin/sh
set -e
python -m daily_leet write-crontab /etc/cron.d/daily-leet
chmod 0644 /etc/cron.d/daily-leet
python -m daily_leet startup
exec cron -f
