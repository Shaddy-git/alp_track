#!/usr/bin/env bash
set -Eeuo pipefail

DB_CONTAINER="alp-track-db"
DB_NAME="appdb"
DB_USER="appuser"
BACKUP_DIR="/var/backups/alp_track"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/${DB_NAME}_docker_${TIMESTAMP}.dump"
TEMP_FILE="${BACKUP_FILE}.tmp"

# Защищённый каталог резервных копий
sudo install -d -o root -g root -m 700 "$BACKUP_DIR"

# Проверка контейнера
if [[ "$(sudo docker inspect -f '{{.State.Running}}' "$DB_CONTAINER")" != "true" ]]; then
    echo "ERROR: PostgreSQL container is not running"
    exit 1
fi

trap 'sudo rm -f "$TEMP_FILE"' EXIT

echo "Creating Docker PostgreSQL backup..."

# Дамп создаётся внутри контейнера, файл сохраняется на Linux-хосте
sudo sh -c '
    umask 077
    docker exec "$1" pg_dump \
        -U "$2" \
        -d "$3" \
        --format=custom \
        --no-owner \
        --no-acl \
        > "$4"
' sh "$DB_CONTAINER" "$DB_USER" "$DB_NAME" "$TEMP_FILE"

# Проверка архива
sudo pg_restore --list "$TEMP_FILE" > /dev/null

# Завершение сохранения
sudo mv "$TEMP_FILE" "$BACKUP_FILE"
sudo chown root:root "$BACKUP_FILE"
sudo chmod 600 "$BACKUP_FILE"

echo "Backup created and verified:"
sudo ls -lh "$BACKUP_FILE"
echo "Backup path: $BACKUP_FILE"
