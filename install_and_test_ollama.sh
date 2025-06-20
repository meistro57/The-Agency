#!/usr/bin/env bash
set -euo pipefail

# install_and_test_ollama.sh
# Installs Ollama if missing, pulls a baseline Qwen model, and runs a quick test.

MODEL=${1:-qwen:7b}

# Install Ollama if not present
if ! command -v ollama >/dev/null 2>&1; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "Ollama already installed."
fi

# Start Ollama server in background if not running
if ! pgrep -f "ollama serve" >/dev/null 2>&1; then
    echo "Starting Ollama server..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    OLLAMA_PID=$!
    # wait a moment for the server to start
    sleep 5
fi

# Pull the specified model
echo "Pulling model $MODEL..."
ollama pull "$MODEL"

# Test the model with a simple prompt
TEST_PROMPT="Hello"
echo "Running test prompt: $TEST_PROMPT"
RESPONSE=$(ollama run "$MODEL" "$TEST_PROMPT" || true)

echo "Model response: $RESPONSE"

# Basic success check
if echo "$RESPONSE" | grep -iq "hello"; then
    echo "Ollama installation verified."
else
    echo "Ollama test failed." >&2
    exit 1
fi

# Stop server if we started it
if [[ -n "${OLLAMA_PID:-}" ]]; then
    kill "$OLLAMA_PID" 2>/dev/null || true
fi
