#!/usr/bin/env bash
set -euo pipefail

# The Agency Ubuntu installation script
# This script installs all dependencies required to run the project on Ubuntu.

# Update package index
sudo apt-get update

# Install system packages
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    mysql-server \
    git \
    curl \
    docker.io

# Start MySQL service
sudo systemctl enable --now mysql

# Set up MySQL database and user
sudo mysql <<MYSQL
CREATE DATABASE IF NOT EXISTS the_agency;
CREATE USER IF NOT EXISTS 'agency'@'localhost' IDENTIFIED BY 'agency123';
GRANT ALL PRIVILEGES ON the_agency.* TO 'agency'@'localhost';
FLUSH PRIVILEGES;
MYSQL

# Set up Python virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

deactivate

# Optional: install Ollama for local model support
curl -fsSL https://ollama.com/install.sh | sh || true

cat <<'MSG'

Installation complete.
Configure API keys and additional settings in environment variables or in config.py before running The Agency.

MSG
