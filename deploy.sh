#!/usr/bin/env bash
set -euo pipefail

# deploy.sh - update repository and launch The Agency

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

echo "Pulling latest code..."
git pull --ff-only

if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

echo "Starting The Agency..."
python interfaces/cli_interface.py
