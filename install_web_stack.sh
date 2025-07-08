#!/usr/bin/env bash
set -euo pipefail

# install_web_stack.sh
# Installs SQLite and Apache for The Agency project.

SQLITE_PKG="sqlite3"
APACHE_PKG="apache2"

sudo apt-get update

install_pkg() {
    if ! dpkg -s "$1" >/dev/null 2>&1; then
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
    else
        echo "$1 already installed."
    fi
}

install_pkg "$SQLITE_PKG"
install_pkg "$APACHE_PKG"

sudo systemctl enable --now apache2

echo "Installation and configuration complete."
