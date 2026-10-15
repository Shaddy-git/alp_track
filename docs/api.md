# API AlpTrack

Базовый URL: `http://localhost:5000/api`

Аутентификация: JWT в заголовке `Authorization: Bearer <token>`.

## Оглавление

- [Авторизация](#авторизация)
- [Пользователи](#пользователи)
- [Горы](#горы)
- [Группы](#группы)
- [Восхождения](#восхождения)
- [Отчёты](#отчёты)
- [Коды ответов](#коды-ответов)

## Авторизация

### POST /auth/register

Регистрация нового пользователя.

**Тело запроса:**
```json
{
  "username": "ivan",
  "email": "ivan@example.com",
  "password": "secret123",
  "full_name": "Иван Иванов",
  "experience_level": 3
}
```

**Ответ 201:**
```json
{
  "message": "Пользователь успешно зарегистрирован",
  "user": {
    "id": 1,
    "username": "ivan",
    "email": "ivan@example.com",
    "full_name": "Иван Иванов",
    "role": "climber",
    "experience_level": 3
  }
}
```

**Ошибки:**
- `400` -- ошибка валидации (короткий пароль, невалидный email).
- `409` -- пользователь с таким username или email уже существует.

### POST /auth/login

Вход в систему.

**Тело запроса:**
```json
{"username": "ivan", "password": "secret123"}
```

**Ответ 200:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {"id": 1, "username": "ivan", "role": "climber", "experience_level": 3}
}
```

**Ошибки:**
- `401` - неверные учётные данные.

### GET /auth/me

Информация о текущем пользователе. **Требует JWT.**

**Ответ 200:**
```json
{"id": 1, "username": "ivan", "email": "ivan@example.com", "full_name": "Иван Иванов", "role": "climber", "experience_level": 3}
```

**Ошибки:**
- `401` - токен отсутствует или невалиден.

## Пользователи

### GET /users

Список всех пользователей. **Только admin.**

**Ответ 200:** массив пользователей.

### GET /users/{id}

Информация о пользователе. **Admin или сам пользователь.**

**Ошибки:**
- `403` - попытка посмотреть чужой профиль.
- `404` - пользователь не найден.

### PUT /users/{id}

Обновление профиля. **Admin или сам пользователь.**

**Тело запроса** (все поля опциональны):
```json
{"full_name": "Новое ФИО", "email": "new@example.com", "experience_level": 4}
```

**Ошибки:**
- `400` - ошибка валидации.
- `403` - чужая попытка редактирования.
- `409` - email уже занят.

### DELETE /users/{id}

Удаление. **Только admin. Нельзя удалить себя.**

### PUT /users/{id}/role

Смена роли. **Только admin. Нельзя менять свою роль.**

**Тело:**
```json
{"role": "instructor"}
```

**Допустимые роли:** `climber`, `instructor`, `admin`.

## Горы

### GET /mountains

Список гор с фильтрами. **Требует JWT.**

**Query-параметры:**
- `min_height` - минимальная высота (int).
- `max_difficulty` - максимальная сложность (1-5).

**Пример:** `GET /mountains?min_height=5000&max_difficulty=3`

**Ответ 200:**
```json
[
  {"id": 15, "name": "Эверест", "height": 8848, "country": "Непал", "difficulty_level": 5},
  {"id": 12, "name": "Эльбрус", "height": 5642, "country": "Россия", "difficulty_level": 3}
]
```

### POST /mountains

Создание. **Только admin.**

**Тело:**
```json
{"name": "Аннапурна", "height": 8091, "country": "Непал", "difficulty_level": 5}
```

**Ошибки:**
- `400` - ошибка валидации.
- `409` - гора с таким названием уже существует.

### PUT /mountains/{id}

Обновление. **Только admin.** Все поля опциональны.

### DELETE /mountains/{id}

Удаление. **Только admin.**

**Ошибки:**
- `404` - гора не найдена.
- `409` - на гору записаны восхождения (защита данных).

## Группы

### GET /groups

Список групп. **Требует JWT.**

### GET /groups/{id}

Детали группы с участниками.

### POST /groups

Создание. **Только instructor/admin.**

**Тело:**
```json
{"name": "Эверест 2026", "start_date": "2026-05-01", "end_date": "2026-05-15", "leader_id": 2}
```

### PUT /groups/{id}

Обновление. **Только instructor/admin.**

### DELETE /groups/{id}

Удаление. **Только admin.**

**Ошибки:**
- `409` - есть связанные восхождения.

### POST /groups/{id}/members

Добавление участника. **Только instructor/admin.**

**Тело:**
```json
{"user_id": 3}
```

**Бизнес-правило:** уровень подготовки пользователя должен быть не ниже сложности горы группы.

**Ошибки:**
- `403` - недостаточный уровень / уже в группе / нельзя присоединиться.
- `404` - пользователь или группа не найдены.

### DELETE /groups/{id}/members/{user_id}

Исключение участника. **Только instructor/admin.**

**Ошибки:**
- `403` - нельзя исключить лидера.
- `400` - пользователь не в группе.

### POST /groups/{id}/join

Самоприсоединение. **Любой Auth.**

Применяются те же бизнес-правила, что и в `POST /members`.

## Восхождения

### GET /ascents

Все восхождения. **Только instructor/admin.**

### GET /ascents/my

Мои восхождения. **Любой Auth.**

### GET /ascents/{id}

Одно восхождение.

### POST /ascents

Создание. **Только instructor/admin.**

**Тело:**
```json
{
  "user_id": 3,
  "mountain_id": 15,
  "group_id": 6,
  "ascent_date": "2026-05-10",
  "is_successful": false,
  "notes": "Test"
}
```

**Бизнес-правила:**
1. Уровень пользователя ≥ сложности горы.
2. Дата восхождения в интервале группы.
3. Нет дубликата (user + mountain + date).

**Ошибки:**
- `400` - ошибка валидации / дубликат.
- `403` - недостаточный уровень / дата вне интервала.

### PUT /ascents/{id}

Обновление. **Только instructor/admin.**

### DELETE /ascents/{id}

Удаление. **Только admin.**

## Отчёты

### GET /reports/climbers-by-mountain/{mountain_id}

Список альпинистов, покоривших гору. **Только instructor/admin.**

**Ответ 200:**
```json
{
  "mountain": {"id": 15, "name": "Эверест", "height": 8848, "difficulty_level": 5},
  "total_ascents": 2,
  "unique_climbers": 2,
  "climbers": [
    {"user_id": 2, "username": "instructor", "first_ascent_date": "2026-05-12"},
    {"user_id": 3, "username": "pro", "first_ascent_date": "2026-05-10"}
  ]
}
```

### GET /reports/successful-ascents?year=2026

Статистика за год. **Только instructor/admin.**

**Ответ 200:**
```json
{
  "year": 2026,
  "total_ascents": 5,
  "successful_ascents": 4,
  "failed_ascents": 1,
  "success_rate": 80.0
}
```

### GET /reports/popular-mountains

Топ гор по числу восхождений. **Только instructor/admin.**

**Query-параметры:**
- `limit` - количество (по умолчанию 5).

### GET /reports/user-stats/{user_id}

Статистика пользователя. **Только instructor/admin.**

## Коды ответов

| Код | Значение |
|-----|----------|
| 200 | OK -- успех |
| 201 | Created -- ресурс создан |
| 400 | Bad Request -- ошибка валидации |
| 401 | Unauthorized -- нет токена или истёк |
| 403 | Forbidden -- недостаточно прав / бизнес-правило |
| 404 | Not Found -- ресурс не найден |
| 409 | Conflict -- конфликт (дубликат, занятый email) |
| 500 | Internal Server Error -- ошибка сервера |