# 🏔️ AlpTrack — система учёта альпинистского клуба

Веб-приложение для учёта гор, альпинистов, групп и восхождений.
Разработано в рамках лабораторной работы №1.

## 🚀 Стек технологий

- **Backend:** Python 3.14, Flask 3.1
- **БД:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.x + Flask-Migrate
- **Авторизация:** JWT (Flask-JWT-Extended)
- **Валидация:** Marshmallow
- **Frontend:** HTML5 + CSS3 + JavaScript

## 📋 Требования

- Python 3.14+
- PostgreSQL 15+
- Git

## 🛠️ Установка окружения (гайд для команды)

### 1. Клонируй репозиторий

```bash
git clone https://github.com/Shaddy-git/alp_track.git
cd alp_track
```

### 2. Создай виртуальное окружение

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установи зависимости

```bash
pip install -r requirements.txt
```

### 4. Настрой переменные окружения

Скопируй шаблон и заполни его:

```bash
cp .env.example .env
```

Открой `.env` и укажи:
- `DATABASE_URL` — строку подключения к PostgreSQL
- `SECRET_KEY` — случайную строку (сгенерируй: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `JWT_SECRET_KEY` — другую случайную строку (тем же способом)

### 5. Создай базу данных в PostgreSQL

```sql
CREATE DATABASE alp_track_db;
CREATE USER alp_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE alp_track_db TO alp_user;
```

### 6. Примени миграции

```bash
cd backend
flask db upgrade
cd ..
```

### 7. Запусти приложение

```bash
cd backend
python app.py
```

Приложение доступно по адресу: http://localhost:5000

### 8. Проверь работоспособность

```bash
curl http://localhost:5000/health
```

Ожидаемый ответ:
```json
{"status": "ok", "database": "connected"}
```

## 📚 Документация

- [Правила внесения изменений](CONTRIBUTING.md)
- [Техническое задание](docs/TZ.md)

## 🛡️ Безопасность

- Пароли хранятся только в виде хешей (`bcrypt`)
- Секреты — только в `.env` (не в Git!)
- Защита от SQL-инъекций через ORM
- Валидация входных данных (Marshmallow)
- JWT-авторизация с ограниченным временем жизни