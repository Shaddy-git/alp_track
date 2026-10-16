#!/usr/bin/env bash
set -euo pipefail
ADMIN_IP="${ADMIN_IP:?Задайте ADMIN_IP=<ip>}"
APP_IP="${APP_IP:-192.168.241.10}"
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from "${ADMIN_IP}" to any port 22 proto tcp
sudo ufw allow from "${APP_IP}" to any port 5432 proto tcp
sudo ufw --force enable
sudo ufw status verbose
