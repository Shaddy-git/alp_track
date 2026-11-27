# Фиксированная версия Python


FROM python:3.14.10-slim-bookworm

LABEL org.opencontainers.image.title="AlpTrack" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.description="AlpTrack application - Laboratory Work 4"




# Настройки Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Рабочая директория
WORKDIR /app

# Создание непривилегированного пользователя
RUN groupadd --system app && \
    useradd --system \
      --gid app \
      --home-dir /app \
      --no-create-home \
      --shell /usr/sbin/nologin \
      app

# Установка зависимостей
COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Копирование проекта
COPY --chown=app:app . /app

# Переход в каталог backend
WORKDIR /app/backend

# Запуск от непривилегированного пользователя
USER app

# Порт приложения
EXPOSE 8000

# Корректная обработка сигнала остановки
STOPSIGNAL SIGTERM

# Запуск Gunicorn
CMD ["gunicorn", "--no-control-socket", "--workers", "2", "--bind", "0.0.0.0:8000", "--access-logfile", "-", "--error-logfile", "-", "app:create_app()"]
