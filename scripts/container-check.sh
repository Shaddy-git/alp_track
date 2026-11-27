#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

DC=(sudo docker compose)
TDC=(sudo docker compose -p alp_track_test -f compose.test.yaml)

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

wait_healthy() {
    local container="$1"

    for i in $(seq 1 30); do
        local state
        state=$(sudo docker inspect \
            -f '{{.State.Health.Status}}' "$container" 2>/dev/null || true)

        echo "$container: ${state:-unknown}"

        [[ "$state" == "healthy" ]] && return 0

        if [[ "$state" == "unhealthy" ]]; then
            sudo docker logs --tail 50 "$container"
            return 1
        fi

        sleep 2
    done

    sudo docker logs --tail 50 "$container"
    return 1
}

echo "========================================"
echo " ALPTRACK CONTAINER CHECK"
echo "========================================"

echo "[1/8] Проверка конфигурации Docker Compose"

"${DC[@]}" config --quiet
"${TDC[@]}" config --quiet

echo "Compose configuration: OK"

echo "[2/8] Проверка Dockerfile и безопасности"

if grep -RniE '(^|[[:space:]])(FROM|image:)[[:space:]]+[^[:space:]]*:latest([[:space:]]|$)' \
    Dockerfile Dockerfile.test compose.yaml compose.test.yaml; then
    fail "Обнаружен тег latest"
fi

grep -Eq '^USER[[:space:]]+app$' Dockerfile ||
    fail "Основное приложение не настроено на пользователя app"

grep -Eq '^USER[[:space:]]+app$' Dockerfile.test ||
    fail "Тестовый контейнер не настроен на пользователя app"

grep -q -- '--no-control-socket' Dockerfile ||
    fail "Не настроено отключение Gunicorn control socket"

grep -q 'healthcheck:' compose.yaml ||
    fail "Не обнаружены healthcheck"

grep -q 'mem_limit:' compose.yaml ||
    fail "Не обнаружены ограничения памяти"

grep -q 'cpus:' compose.yaml ||
    fail "Не обнаружены ограничения CPU"

grep -q '127.0.0.1:8001:8000' compose.yaml ||
    fail "Не найдено ограничение публикации порта приложения"

if grep -Eq '^[[:space:]]*-[[:space:]]*"?[^"]*5432:[0-9]+' compose.yaml; then
    fail "Обнаружена публикация порта PostgreSQL"
fi

echo "Dockerfile security: OK"

echo "[3/8] Сборка образов"

"${DC[@]}" build app
"${TDC[@]}" build test-runner

echo "Image build: OK"

echo "[4/8] Проверка образов"

APP_USER=$(sudo docker image inspect \
    --format '{{.Config.User}}' alp-track-app:0.1.0)

TEST_USER=$(sudo docker image inspect \
    --format '{{.Config.User}}' alp-track-test:0.1.0)

[[ "$APP_USER" == "app" ]] ||
    fail "Основной образ работает не от app"

[[ "$TEST_USER" == "app" ]] ||
    fail "Тестовый образ работает не от app"

IMAGE_ENV=$(sudo docker image inspect \
    --format '{{json .Config.Env}}' alp-track-app:0.1.0)

if grep -Eq 'DATABASE_URL|SECRET_KEY|JWT_SECRET_KEY' <<< "$IMAGE_ENV"; then
    fail "Обнаружены секретные переменные в образе"
fi

sudo docker run --rm --entrypoint sh alp-track-app:0.1.0 \
    -c 'test ! -e /app/.env && test ! -e /app/.env.test' ||
    fail "В образ попали локальные файлы конфигурации"

echo "Image security: OK"

echo "[5/8] Проверка основного окружения"

"${DC[@]}" up -d db app

wait_healthy alp-track-db ||
    fail "PostgreSQL не стал healthy"

wait_healthy alp-track-app ||
    fail "Приложение не стало healthy"

APP_UID=$(sudo docker exec alp-track-app id -u)

[[ "$APP_UID" != "0" ]] ||
    fail "Приложение запущено от root"

DB_HOST_PORTS=$(sudo docker inspect alp-track-db \
    --format '{{range $p, $conf := .NetworkSettings.Ports}}{{if $conf}}{{range $conf}}{{.HostPort}}{{end}}{{end}}{{end}}')

[[ -z "$DB_HOST_PORTS" ]] ||
    fail "PostgreSQL опубликован на хосте"

DB_VOLUME=$(sudo docker inspect alp-track-db \
    --format '{{range .Mounts}}{{if eq .Destination "/var/lib/postgresql/data"}}{{.Name}}{{end}}{{end}}')

[[ "$DB_VOLUME" == "alp_track_pgdata" ]] ||
    fail "Основной PostgreSQL Volume отсутствует"

HEALTH=$(curl -fsS http://127.0.0.1:8001/health)

python3 -c '
import json, sys
data = json.loads(sys.argv[1])
assert data.get("status") == "ok", data
assert data.get("database") == "connected", data
' "$HEALTH" || fail "Проверка /health не пройдена"

HTTP_CODE=$(curl -s -o /dev/null -w '%{http_code}' \
    http://127.0.0.1:8001/)

[[ "$HTTP_CODE" == "200" ]] ||
    fail "Frontend вернул HTTP $HTTP_CODE"

echo "Main environment: OK"

echo "[6/8] Подготовка изолированной тестовой БД"

if sudo docker volume inspect alp_track_test_pgdata >/dev/null 2>&1; then
    fail "Тестовый Volume уже существует. Проверь его перед запуском."
fi

TEST_STACK_STARTED=1

cleanup() {
    local result=$?
    trap - EXIT

    if [[ "$TEST_STACK_STARTED" == "1" ]]; then
        echo "Удаление временной тестовой среды..."
        "${TDC[@]}" \
            down -v --remove-orphans || \
            echo "WARNING: проверь остатки тестовой среды"
    fi

    exit "$result"
}

trap cleanup EXIT

"${TDC[@]}" up -d test-db

TEST_DB_ID=$("${TDC[@]}" ps -q test-db)
[[ -n "$TEST_DB_ID" ]] || fail "Тестовый PostgreSQL-контейнер не найден"
wait_healthy "$TEST_DB_ID" ||
    fail "Тестовая PostgreSQL не стала healthy"

echo "[7/8] Запуск миграций, Ruff, Bandit и Pytest"

"${TDC[@]}" run --rm --no-deps test-runner

echo "[8/8] Итоговая проверка"

sudo docker volume inspect alp_track_pgdata >/dev/null ||
    fail "Основной Volume потерян"

HEALTH=$(curl -fsS http://127.0.0.1:8001/health)

echo "Основная БД: $HEALTH"
echo "Тестовая среда будет удалена автоматически."

TEST_STACK_STARTED=0
"${TDC[@]}" down -v --remove-orphans

trap - EXIT

echo "========================================"
echo " CONTAINER CHECK PASSED"
echo "========================================"
