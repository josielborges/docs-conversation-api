#!/bin/bash

# Start script for Docs Conversation API

echo "Starting Docs Conversation API..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Run migrations
echo "Running database migrations..."
uv run alembic upgrade head

# Start the server
echo "Starting server..."
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
