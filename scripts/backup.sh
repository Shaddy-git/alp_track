#!/usr/bin/env bash
set -euo pipefail

DB_NAME="appdb"
BACKUP_DIR="$HOME/alptrack-backups"

umask 077
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.dump"
TEMP_FILE="${BACKUP_FILE}.tmp"

trap 'rm -f "$TEMP_FILE"' EXIT

echo "Creating backup of $DB_NAME..."

sudo -u postgres pg_dump \
    --dbname="$DB_NAME" \
    --format=custom \
    --no-owner \
    --no-privileges > "$TEMP_FILE"

if ! pg_restore --list "$TEMP_FILE" > /dev/null; then
    echo "ERROR: Invalid backup archive"
    exit 1
fi

mv "$TEMP_FILE" "$BACKUP_FILE"

echo "Backup created successfully:"
ls -lh "$BACKUP_FILE"