#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$PROJECT_ROOT"

echo "=== Alp_track: Initial Setup ==="

if ! command -v python3 >/dev/null 2>$&1; then
    echo "ERROR: Python3 is not installed"
    exit 1
fi

python3 --version

if [! -x ".venv/bin/python" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

PYTHON="$PROJECT_ROOT/.venv/bin/python"

echo "Installing dependencies..."
"$PYTHON" -m pip install -r requirements-dev.txt

if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "Created .env from .env.example"
        echo "IMPORTANT: Configure database and secrets in .env"
    else
        echo "WARNING: .env.example was not found"
    fi
fi

echo "=== Setup completed successfully ==="