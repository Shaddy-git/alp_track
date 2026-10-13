from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from marshmallow import ValidationError

from schemas.auth import RegisterSchema, LoginSchema
from services.auth_service import register_user, authenticate_user, get_user_by_id

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """Регистрация нового пользователя."""
    schema = RegisterSchema()
    
    # Валидация входных данных
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({
            "error": "Ошибка валидации",
            "details": err.messages
        }), 400
    
    # Вызов сервиса
    try:
        user = register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            experience_level=data.get('experience_level', 1)
        )
    except ValueError as err:
        return jsonify({"error": str(err)}), 409
    
    return jsonify({
        "message": "Пользователь успешно зарегистрирован",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "experience_level": user.experience_level
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Вход в систему — возвращает JWT."""
    schema = LoginSchema()
    
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({
            "error": "Ошибка валидации",
            "details": err.messages
        }), 400
    
    user = authenticate_user(data['username'], data['password'])
    
    if not user:
        # Намеренно не уточняем, что именно неверно
        return jsonify({"error": "Неверные учётные данные"}), 401
    
    # Генерируем JWT. identity должен быть строкой!
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "experience_level": user.experience_level
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Информация о текущем пользователе (требует JWT)."""
    user_id = get_jwt_identity()
    user = get_user_by_id(int(user_id))
    
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "experience_level": user.experience_level
    }), 200