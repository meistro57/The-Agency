#!/usr/bin/env bash
set -euo pipefail

# deploy.sh - update repository and launch The Agency

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "Pulling latest code..."
git pull --ff-only

# Ensure virtual environment exists
if [ ! -f ".venv/bin/activate" ]; then
    echo "Virtual environment not found. Running setup..."
    ./setup.sh
fi

echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies each run in case requirements changed
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Launching web dashboard..."
python interfaces/web_dashboard.py &
DASHBOARD_PID=$!

# Give the server a moment to start before opening the browser
sleep 2
URL="http://localhost:5000"
if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 &
elif command -v open >/dev/null 2>&1; then
    open "$URL" >/dev/null 2>&1 &
fi

echo "Starting The Agency CLI..."
python interfaces/cli_interface.py

# Stop the dashboard when the CLI exits
kill "$DASHBOARD_PID" 2>/dev/null || true
