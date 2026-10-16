#!/usr/bin/env bash
set -euo pipefail
DB_IP="${DB_IP:-192.168.241.20}"
APP_IP="${APP_IP:-192.168.241.10}"
PG_VERSION="${PG_VERSION:-17}"
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
CONF="/etc/postgresql/${PG_VERSION}/main/postgresql.conf"
HBA="/etc/postgresql/${PG_VERSION}/main/pg_hba.conf"
sudo sed -i "s|^#\?listen_addresses.*|listen_addresses = 'localhost,${DB_IP}'|" "$CONF"
if ! sudo grep -q "appuser.*${APP_IP}/32" "$HBA"; then
    echo "host appdb appuser ${APP_IP}/32 scram-sha-256" | sudo tee -a "$HBA"
fi
sudo systemctl restart postgresql
sudo ss -tulpn | grep 5432 || true
