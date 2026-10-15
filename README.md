# AlpTrack - система учёта альпинистского клуба

Веб-приложение для централизованного учёта гор, альпинистов, групп и восхождений.
Разработано в рамках лабораторной работы №1 по дисциплине «Методологии и практики DevOps».

## 🎯 Возможности

- Регистрация и вход пользователей (JWT-авторизация).
- Разграничение прав доступа (RBAC): `climber`, `instructor`, `admin`.
- Управление справочником гор (CRUD с фильтрами).
- Управление группами и участниками (связь M:N).
- Учёт восхождений с автоматической проверкой уровня подготовки.
- Валидация дат: восхождение должно попадать в интервал группы.
- Отчёты: топ гор, статистика за год, покорители вершин.
- Веб-интерфейс: лендинг, регистрация, вход, личный кабинет, каталог гор, отчёты.

## 🚀 Стек технологий

- **Backend:** Python 3.14, Flask 3.1
- **БД:** PostgreSQL 15+
- **ORM:** SQLAlchemy 2.x + Flask-Migrate
- **Авторизация:** JWT (Flask-JWT-Extended)
- **Валидация:** Marshmallow
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Bootstrap 5

## 📋 Требования

- Python 3.14+
- PostgreSQL 15+
- Git

## 🛠️ Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/Shaddy-git/alp_track.git
cd alp_track
```

### 2. Создать виртуальное окружение

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

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения

Скопируй шаблон:

```bash
cp .env.example .env
```

Открой `.env` и заполни:

```env
DATABASE_URL=postgresql://alp_user:ПАРОЛЬ@localhost:5432/alp_track_db
SECRET_KEY=<сгенерируй: python -c "import secrets; print(secrets.token_hex(32))">
JWT_SECRET_KEY=<сгенерируй ещё раз>
```

### 5. Создать базу данных в PostgreSQL

```sql
CREATE DATABASE alp_track_db;
CREATE USER alp_user WITH PASSWORD 'ПАРОЛЬ';
GRANT ALL PRIVILEGES ON DATABASE alp_track_db TO alp_user;
```

**Пароль здесь должен совпадать с тем, что в `.env`.**

### 6. Применить миграции

```bash
python -m flask db upgrade
```

### 7. Запустить backend

```bash
python manage.py
```

Backend доступен: `http://localhost:5000`

Проверка:

```bash
curl.exe http://localhost:5000/health
```

Ожидаемый ответ:
```json
{"status": "ok", "database": "connected"}
```

### 8. Запустить frontend

**В отдельном терминале:**

```bash
cd frontend
python -m http.server 8080
```

Frontend доступен: `http://localhost:8080`

## 🌐 Страницы сайта

| Страница | URL | Что показывает |
|----------|-----|----------------|
| Лендинг | `/index.html` | Описание системы |
| Регистрация | `/register.html` | Форма регистрации |
| Вход | `/login.html` | Форма входа |
| Личный кабинет | `/dashboard.html` | Профиль, мои восхождения, группы, горы |
| Каталог гор | `/mountains.html` | Список гор с фильтрами |
| Отчёты | `/reports.html` | Топ гор, статистика, покорители (только instructor/admin) |

## 📡 API

### Авторизация

| Метод | URL | Описание | Роль |
|-------|-----|----------|------|
| POST | `/api/auth/register` | Регистрация | — |
| POST | `/api/auth/login` | Вход (JWT) | — |
| GET | `/api/auth/me` | Текущий пользователь | Auth |

**Пример регистрации:**

```bash
curl.exe -X POST http://localhost:5000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"ivan\",\"email\":\"ivan@example.com\",\"password\":\"secret123\",\"experience_level\":3}"
```

**Пример входа:**

```bash
curl.exe -X POST http://localhost:5000/api/auth/login ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"ivan\",\"password\":\"secret123\"}"
```

**Ответ:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {"id": 1, "username": "ivan", "role": "climber", "experience_level": 3}
}
```

### Горы

| Метод | URL | Описание | Роль |
|-------|-----|----------|------|
| GET | `/api/mountains` | Список (с фильтрами) | Auth |
| GET | `/api/mountains/{id}` | Одна гора | Auth |
| POST | `/api/mountains` | Создать | admin |
| PUT | `/api/mountains/{id}` | Обновить | admin |
| DELETE | `/api/mountains/{id}` | Удалить (защита от восхождений) | admin |

### Восхождения

| Метод | URL | Описание | Роль |
|-------|-----|----------|------|
| GET | `/api/ascents` | Все восхождения | instructor/admin |
| GET | `/api/ascents/my` | Мои восхождения | Auth |
| POST | `/api/ascents` | Создать (с бизнес-правилами) | instructor/admin |
| PUT | `/api/ascents/{id}` | Обновить | instructor/admin |
| DELETE | `/api/ascents/{id}` | Удалить | admin |

### Группы

| Метод | URL | Описание | Роль |
|-------|-----|----------|------|
| GET | `/api/groups` | Список | Auth |
| GET | `/api/groups/{id}` | Одна с участниками | Auth |
| POST | `/api/groups` | Создать | instructor/admin |
| PUT | `/api/groups/{id}` | Обновить | instructor/admin |
| DELETE | `/api/groups/{id}` | Удалить (защита от восхождений) | admin |
| POST | `/api/groups/{id}/members` | Добавить участника | instructor/admin |
| DELETE | `/api/groups/{id}/members/{user_id}` | Исключить участника | instructor/admin |
| POST | `/api/groups/{id}/join` | Присоединиться | Auth |

### Пользователи

| Метод | URL | Описание | Роль |
|-------|-----|----------|------|
| GET | `/api/users` | Список | admin |
| GET | `/api/users/{id}` | Один | admin / self |
| PUT | `/api/users/{id}` | Обновить | admin / self |
| DELETE | `/api/users/{id}` | Удалить | admin |
| PUT | `/api/users/{id}/role` | Сменить роль | admin |

### Отчёты

| Метод | URL | Описание | Роль |
|-------|-----|----------|------|
| GET | `/api/reports/climbers-by-mountain/{id}` | Покорители горы | instructor/admin |
| GET | `/api/reports/successful-ascents?year=2026` | Статистика за год | instructor/admin |
| GET | `/api/reports/popular-mountains` | Топ гор | instructor/admin |
| GET | `/api/reports/user-stats/{id}` | Статистика пользователя | instructor/admin |

## 🛡️ Безопасность

- **Пароли** хранятся только в виде хешей (`werkzeug.security`, scrypt).
- **JWT-авторизация** с временем жизни 1 час.
- **RBAC:** 3 роли - `climber`, `instructor`, `admin`.
- **Защита от SQL-инъекций** через ORM (SQLAlchemy).
- **Валидация входных данных** (Marshmallow).
- **CORS** настроен для frontend.
- **Секреты** - только в `.env`, не в Git.
- **Каскадные удаления с защитой:** нельзя удалить гору/группу, если на неё есть восхождения.
- **Защита от дублирования** восхождений (user + mountain + date).
- **Проверка уровня подготовки** - нельзя идти на гору, если уровень ниже сложности.

## 📁 Структура проекта

```
alp_track/
├── backend/                  # Flask-приложение
│   ├── __init__.py
│   ├── app.py                # Фабрика приложения
│   ├── config.py             # Конфигурация
│   ├── extensions.py         # Расширения (db, jwt, migrate)
│   ├── models/               # Модели БД (SQLAlchemy)
│   │   ├── user.py
│   │   ├── mountain.py
│   │   ├── group.py
│   │   └── ascent.py
│   ├── schemas/              # Marshmallow-схемы
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── mountain.py
│   │   ├── group.py
│   │   └── ascent.py
│   ├── routes/               # API-эндпоинты (blueprints)
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── mountains.py
│   │   ├── groups.py
│   │   ├── ascents.py
│   │   └── reports.py
│   ├── services/             # Бизнес-логика
│   │   ├── auth_service.py
│   │   └── ascent_service.py
│   ├── utils/                # Утилиты
│   │   └── decorators.py     # @role_required
│   └── migrations/           # Миграции Flask-Migrate
├── frontend/                 # Веб-интерфейс
│   ├── index.html            # Лендинг
│   ├── login.html            # Вход
│   ├── register.html         # Регистрация
│   ├── dashboard.html        # Личный кабинет
│   ├── mountains.html        # Каталог гор
│   ├── reports.html          # Отчёты
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── api.js            # Обёртка над fetch
│       ├── login.js
│       ├── register.js
│       ├── dashboard.js
│       ├── mountains.js
│       └── reports.js
├── docs/
│   ├── TZ.md                 # Техническое задание
│   └── api.md                # Детальное описание API
├── manage.py                 # Точка входа Flask CLI
├── requirements.txt          # Зависимости
├── README.md                 # Этот файл
├── CONTRIBUTING.md           # Правила внесения изменений
├── .env.example              # Шаблон секретов
└── .gitignore
```

## 📚 Документация

- [Правила внесения изменений](CONTRIBUTING.md)
- [Техническое задание](docs/TZ.md)
- [Детальное описание API](docs/api.md)

## 🎯 Версии

- **v0.1.0** - первая версия: полный CRUD, RBAC, бизнес-правила, веб-интерфейс.