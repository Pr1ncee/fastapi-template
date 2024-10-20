#! /usr/bin/env sh

set -euf

export PYTHONPATH="${PYTHONPATH}:/app"

echo "Applying migrations..."
alembic --config /app/src/alembic.ini upgrade head

echo "Starting the application..."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
