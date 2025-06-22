#!/usr/bin/env bash
set -euo pipefail

# install_web_stack.sh
# Installs and configures MySQL, phpMyAdmin, and Apache for The Agency project.

MYSQL_PKG="mysql-server"
PHPMYADMIN_PKG="phpmyadmin"
APACHE_PKG="apache2"

DB_NAME="${MYSQL_DATABASE:-the_agency}"
DB_USER="${MYSQL_USER:-agency}"
DB_PASS="${MYSQL_PASSWORD:-agency123}"

sudo apt-get update

install_pkg() {
    if ! dpkg -s "$1" >/dev/null 2>&1; then
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y "$@"
    else
        echo "$1 already installed."
    fi
}

install_pkg "$MYSQL_PKG"
install_pkg "$APACHE_PKG"
install_pkg "$PHPMYADMIN_PKG" php-mysql

sudo systemctl enable --now mysql
sudo systemctl enable --now apache2

sudo mysql <<MYSQL
CREATE DATABASE IF NOT EXISTS $DB_NAME;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
MYSQL

# Basic tests
mysql -u "$DB_USER" -p"$DB_PASS" -e "SELECT 1;" "$DB_NAME"

if curl -s -o /dev/null -w "%{http_code}" http://localhost/phpmyadmin/ | grep -q 200; then
    echo "phpMyAdmin reachable."
else
    echo "phpMyAdmin test failed" >&2
    exit 1
fi

echo "Installation and configuration complete."
