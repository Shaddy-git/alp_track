#!/usr/bin/env bash
set -euo pipefail
cd /opt/myapp
set -a
. /etc/myapp/app.env
set +a
unset FLASK_APP
export PYTHONPATH=/opt/myapp/backend
exec /opt/myapp/venv/bin/python -m flask --app app:create_app db upgrade
