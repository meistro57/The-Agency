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

echo "Starting The Agency..."
python interfaces/cli_interface.py
