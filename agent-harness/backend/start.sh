#!/bin/bash
# Start the Activepieces Flow Agent backend
# Usage: ./start.sh [port]

PORT=${1:-8181}
cd "$(dirname "$0")"

if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found. Copy .env.example and add your ANTHROPIC_API_KEY."
    exit 1
fi

echo "Starting Flow Agent backend on port $PORT..."
python3 -m uvicorn main:app --host 0.0.0.0 --port "$PORT" --reload
