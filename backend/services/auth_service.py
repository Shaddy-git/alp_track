from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db
from models.user import User


def register_user(username: str, email: str, password: str, experience_level: int = 1,  full_name: str = None) -> User:
    """Регистрирует нового пользователя.
    
    Raises:
        ValueError: если пользователь с таким username или email уже существует.
    """
    # Проверка уникальности username
    if User.query.filter_by(username=username).first():
        raise ValueError("Пользователь с таким именем уже существует")
    
    # Проверка уникальности email
    if User.query.filter_by(email=email).first():
        raise ValueError("Пользователь с таким email уже существует")
    
    # Создание пользователя с хешем пароля
    user = User(
        username=username,
        email=email,
        full_name=full_name,
        password_hash=generate_password_hash(password),
        experience_level=experience_level,
        role='climber'  # по умолчанию - обычный альпинист
    )
    
    db.session.add(user)
    db.session.commit()
    
    return user


def authenticate_user(username: str, password: str) -> User | None:
    """Проверяет учётные данные.
    
    Returns:
        User, если учётные данные верны, иначе None.
    """
    user = User.query.filter_by(username=username).first()
    
    # ВАЖНО: проверяем одинаково и для несуществующего пользователя,
    # и для неверного пароля - чтобы не давать подсказок атакующему
    if not user:
        return None
    
    if not check_password_hash(user.password_hash, password):
        return None
    
    return user


def get_user_by_id(user_id: int) -> User | None:
    """Возвращает пользователя по ID."""
    return User.query.get(user_id)