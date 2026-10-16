#!/usr/bin/env bash
set -euo pipefail
echo "==> systemctl status myapp"
systemctl status myapp --no-pager || true
echo
echo "==> Порты"
sudo ss -tulpn | grep -E ':8000|:5432' || true
echo
echo "==> health-check"
curl -sf http://127.0.0.1:8000/health && echo || echo "FAIL"
echo
echo "==> Последние строки журнала"
journalctl -u myapp -n 20 --no-pager || true
