#!/usr/bin/env bash
set -euo pipefail
sudo apt update
sudo apt install -y python3 python3-venv python3-pip python3-dev libpq-dev gcc build-essential postgresql-client curl ufw
if ! id appuser >/dev/null 2>&1; then
    sudo adduser --system --group --no-create-home --shell /usr/sbin/nologin appuser
fi
sudo mkdir -p /opt/myapp /etc/myapp /var/log/myapp /var/lib/myapp
sudo chown -R root:appuser /opt/myapp
sudo chmod 750 /opt/myapp
sudo chown root:appuser /etc/myapp
sudo chmod 750 /etc/myapp
sudo chown -R appuser:appuser /var/log/myapp /var/lib/myapp
sudo chmod 750 /var/log/myapp /var/lib/myapp
