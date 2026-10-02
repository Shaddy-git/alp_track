# backend/config.py
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Базовая конфигурация приложения.
    
    Все секреты читаются из .env — они не должны быть в коде.
    """
    # Строка подключения к PostgreSQL
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    
    # Отключаем отслеживание модификаций (экономит память)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Секретный ключ приложения (для сессий, CSRF, flash)
    SECRET_KEY = os.getenv("SECRET_KEY")
    
    # Секретный ключ для JWT-токенов
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    
    # Время жизни access-токена: 1 час
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    
    # Режим отладки (в продакшене — False)
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"