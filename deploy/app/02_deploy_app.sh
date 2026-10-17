#!/usr/bin/env bash
set -euo pipefail
APP_DIR="${APP_DIR:-/opt/myapp}"
VENV="${VENV:-/opt/myapp/venv}"
cd "$APP_DIR"
if [ ! -d "$VENV" ]; then
    sudo python3 -m venv "$VENV"
    sudo chown -R appuser:appuser "$VENV"
fi
sudo -u appuser "$VENV/bin/pip" install --upgrade pip
sudo -u appuser "$VENV/bin/pip" install -r "$APP_DIR/requirements.txt"
sudo -u appuser "$VENV/bin/python" -c "import flask, sqlalchemy, psycopg2; print('Imports OK')"
