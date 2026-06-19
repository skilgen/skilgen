#!/bin/sh
set -eu

if [ -n "${DATABASE_URL:-}" ]; then
  echo "Running API migrations..."
  alembic -c /app/apps/api/alembic.ini upgrade head
else
  echo "DATABASE_URL is not set; skipping API migrations."
fi

exec "$@"
