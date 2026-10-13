from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

from models.user import User


def role_required(*allowed_roles):
    """Декоратор, разрешающий доступ только пользователям с определённой ролью.
    
    Использование:
        @role_required('admin')
        @role_required('admin', 'instructor')
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # Проверяем JWT (аналог @jwt_required())
            verify_jwt_in_request()
            
            # Получаем пользователя из БД
            user_id = get_jwt_identity()
            user = User.query.get(int(user_id))
            
            if not user:
                return jsonify({"error": "Пользователь не найден"}), 404
            
            if user.role not in allowed_roles:
                # 403 Forbidden - пользователь аутентифицирован, но у него нет прав
                return jsonify({"error": "Недостаточно прав"}), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator