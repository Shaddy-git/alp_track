from extensions import db
from models.user import User
from models.mountain import Mountain
from models.group import Group
from models.ascent import Ascent


def can_climber_join_group(user_id: int, group_id: int) -> tuple[bool, str]:
    """Проверяет, может ли альпинист присоединиться к группе.
    
    Бизнес-правило: уровень подготовки альпиниста (experience_level)
    должен быть не ниже сложности горы (difficulty_level), на которую
    планируется восхождение группы.
    
    Returns:
        (True, "") - если можно.
        (False, "причина") - если нельзя.
    """
    user = User.query.get(user_id)
    if not user:
        return False, "Пользователь не найден"
    
    group = Group.query.get(group_id)
    if not group:
        return False, "Группа не найдена"
    
    # Проверка: пользователь уже в группе?
    if user in group.members:
        return False, "Пользователь уже состоит в этой группе"
    
    # Проверка: статус группы позволяет присоединиться?
    if group.status not in ('planning', 'active'):
        return False, f"Нельзя присоединиться к группе со статусом '{group.status}'"
    
    # БИЗНЕС-ПРАВИЛО: проверка уровня подготовки
    # Находим самую сложную гору, на которую идёт группа.
    # Если у группы нет восхождений, берём максимальную сложность по её ascents.
    ascents = Ascent.query.filter_by(group_id=group_id).all()
    
    if not ascents:
        return False, "У группы ещё нет запланированных восхождений"
    
    max_difficulty = max(a.mountain.difficulty_level for a in ascents)
    
    if user.experience_level < max_difficulty:
        return False, (
            f"Недостаточный уровень подготовки: "
            f"у вас {user.experience_level}, требуется минимум {max_difficulty}"
        )
    
    return True, ""


def add_climber_to_group(user_id: int, group_id: int) -> tuple[bool, str]:
    """Добавляет альпиниста в группу с проверкой бизнес-правил.
    
    Returns:
        (True, "") - при успехе.
        (False, "причина") - при отказе.
    """
    can_join, reason = can_climber_join_group(user_id, group_id)
    if not can_join:
        return False, reason
    
    user = User.query.get(user_id)
    group = Group.query.get(group_id)
    
    group.members.append(user)
    db.session.commit()
    
    return True, "Пользователь добавлен в группу"

def validate_ascent_dates(group_id: int, ascent_date) -> tuple[bool, str]:
    """Проверяет, что дата восхождения попадает в интервал группы.
    
    Бизнес-правило из ТЗ, п. 4.4.2:
    Дата восхождения не может быть раньше даты начала группы
    или позже даты окончания.
    
    Returns:
        (True, "") - если валидна.
        (False, "причина") - если нет.
    """
    if not group_id:
        # Если группа не указана - валидация не применяется
        return True, ""
    
    group = Group.query.get(group_id)
    if not group:
        return False, "Группа не найдена"
    
    if ascent_date < group.start_date:
        return False, (
            f"Дата восхождения ({ascent_date}) раньше даты начала группы "
            f"({group.start_date})"
        )
    
    if ascent_date > group.end_date:
        return False, (
            f"Дата восхождения ({ascent_date}) позже даты окончания группы "
            f"({group.end_date})"
        )
    
    return True, ""


def create_ascent(user_id: int, mountain_id: int, group_id, ascent_date,
                  is_successful: bool = False, notes: str = None) -> tuple[bool, str, Ascent | None]:
    """Создаёт восхождение с проверкой всех правил.
    
    Returns:
        (True, "", Ascent) - при успехе.
        (False, "причина", None) - при ошибке.
    """
    # Проверка: пользователь существует
    user = User.query.get(user_id)
    if not user:
        return False, "Пользователь не найден", None
    
    # Проверка: гора существует
    mountain = Mountain.query.get(mountain_id)
    if not mountain:
        return False, "Гора не найдена", None
    
    # Бизнес-правило: уровень подготовки
    if user.experience_level < mountain.difficulty_level:
        return False, (
            f"Недостаточный уровень подготовки: у вас {user.experience_level}, "
            f"требуется минимум {mountain.difficulty_level}"
        ), None
    
    # Бизнес-правило: валидация дат
    dates_ok, dates_error = validate_ascent_dates(group_id, ascent_date)
    if not dates_ok:
        return False, dates_error, None

    # Проверка: такое восхождение уже существует?
    existing = Ascent.query.filter_by(
        user_id=user_id,
        mountain_id=mountain_id,
        ascent_date=ascent_date
    ).first()
    
    if existing:
        return False, (
            f"Восхождение {user.username} на {mountain.name} "
            f"от {ascent_date} уже зафиксировано (id={existing.id})"
        ), None
    
    # Создание
    ascent = Ascent(
        user_id=user_id,
        mountain_id=mountain_id,
        group_id=group_id,
        ascent_date=ascent_date,
        is_successful=is_successful,
        notes=notes
    )
    
    db.session.add(ascent)
    db.session.commit()
    
    return True, "Восхождение создано", ascent