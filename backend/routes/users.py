from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models.user import User
from schemas.user import UserUpdateSchema, UserRoleSchema
from utils.decorators import role_required

users_bp = Blueprint('users', __name__)


@users_bp.route('', methods=['GET'])
@role_required('admin')
def list_users():
    """Список всех пользователей. Только для admin."""
    users = User.query.order_by(User.id).all()
    
    return jsonify([{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "full_name": u.full_name,
        "role": u.role,
        "experience_level": u.experience_level
    } for u in users]), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Информация о пользователе.
    
    Доступ: admin - любого, обычный пользователь - только своего.
    """
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    # Проверка прав: admin или сам себя
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({"error": "Недостаточно прав"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "experience_level": user.experience_level
    }), 200


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Обновить профиль пользователя.
    
    Доступ: admin - любого, обычный - только своего.
    Нельзя менять роль через этот эндпоинт - для этого есть /role.
    """
    current_user_id = int(get_jwt_identity())
    current_user = User.query.get(current_user_id)
    
    # Проверка прав
    if current_user.role != 'admin' and current_user_id != user_id:
        return jsonify({"error": "Недостаточно прав"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    schema = UserUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    # Проверка уникальности email, если меняется
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({"error": "Пользователь с таким email уже существует"}), 409
    
    # Обновление полей
    for field in ['full_name', 'email', 'experience_level']:
        if field in data:
            setattr(user, field, data[field])
    
    db.session.commit()
    
    return jsonify({
        "message": "Профиль обновлён",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "experience_level": user.experience_level
        }
    }), 200


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """Удалить пользователя. Только для admin.
    
    Нельзя удалить самого себя.
    """
    current_user_id = int(get_jwt_identity())
    
    if current_user_id == user_id:
        return jsonify({"error": "Нельзя удалить самого себя"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({"message": "Пользователь удалён"}), 200


@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@role_required('admin')
def change_role(user_id):
    """Сменить роль пользователя. Только для admin.
    
    Нельзя сменить роль самому себе.
    """
    current_user_id = int(get_jwt_identity())
    
    if current_user_id == user_id:
        return jsonify({"error": "Нельзя менять свою роль"}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    schema = UserRoleSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    user.role = data['role']
    db.session.commit()
    
    return jsonify({
        "message": f"Роль изменена на '{data['role']}'",
        "user_id": user.id,
        "new_role": user.role
    }), 200