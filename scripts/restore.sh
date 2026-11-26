#!/usr/bin/env bash
set -euo pipefail

TARGET_DB="appdb_restore_lab3"
BACKUP_FILE="${1:-}"

# Check selected backup file
if [[ -z "$BACKUP_FILE" || ! -f "$BACKUP_FILE" ]]; then
    echo "Usage: bash restore.sh <backup-file>"
    exit 1
fi

# Verify archive before restoration
pg_restore --list "$BACKUP_FILE" > /dev/null

# Protect existing databases
DB_EXISTS=$(sudo -u postgres psql \
    -d postgres -tAc \
    "SELECT 1 FROM pg_database WHERE datname='$TARGET_DB'")

if [[ "$DB_EXISTS" == "1" ]]; then
    echo "ERROR: Database $TARGET_DB already exists"
    echo "Existing database will not be modified"
    exit 1
fi

echo "Backup file: $BACKUP_FILE"
echo "Target database: $TARGET_DB"
echo "Production database appdb will not be modified"

read -r -p "Type RESTORE to continue: " CONFIRM

if [[ "$CONFIRM" != "RESTORE" ]]; then
    echo "Restore cancelled"
    exit 1
fi

# Create a separate empty database
sudo -u postgres createdb \
    --template=template0 \
    "$TARGET_DB"

# Restore schema and data
# The archive is read by the current Linux user
sudo -u postgres pg_restore \
    --dbname="$TARGET_DB" \
    --no-owner \
    --no-privileges \
    --single-transaction \
    --exit-on-error < "$BACKUP_FILE"

echo "Database restored successfully"

# Show restored tables
sudo -u postgres psql -d "$TARGET_DB" -c '\dt'