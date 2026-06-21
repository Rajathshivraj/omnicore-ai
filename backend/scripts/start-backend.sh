#!/bin/sh
set -eu

if [ "${OMNICORE_RUN_MIGRATIONS:-true}" = "true" ]; then
  /app/scripts/init-db.sh
fi

if [ "${OMNICORE_SEED_DATABASE:-true}" = "true" ]; then
  /app/scripts/seed-db.sh
fi

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
