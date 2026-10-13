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
        (True, "") — если можно.
        (False, "причина") — если нельзя.
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