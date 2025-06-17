#!/usr/bin/env bash
set -e

# Basic setup script for The Agency
# Creates Python virtual environment, installs dependencies,
# ensures Ollama is available and downloads a base model.

# create venv if not exists
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

deactivate

# Check for Ollama
if command -v ollama >/dev/null 2>&1; then
    echo "Ollama detected. Using existing installation."
else
    echo "Ollama not found. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Download base model defined by $OLLAMA_MODEL or default qwen:7b
MODEL_NAME=${OLLAMA_MODEL:-qwen:7b}
ollama pull "$MODEL_NAME"

# Create .env with default Ollama settings if not present
if [ ! -f .env ]; then
    cat <<EOT > .env
OLLAMA_MODEL=$MODEL_NAME
OLLAMA_API_URL=http://localhost:11434
EOT
    echo ".env file created with Ollama defaults."
fi

echo "Setup complete. Activate the virtual environment with 'source .venv/bin/activate' before running The Agency."
