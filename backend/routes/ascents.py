from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models.ascent import Ascent
from models.mountain import Mountain
from models.user import User
from schemas.ascent import AscentSchema, AscentUpdateSchema
from services.ascent_service import create_ascent, validate_ascent_dates
from utils.decorators import role_required

ascents_bp = Blueprint('ascents', __name__)


@ascents_bp.route('', methods=['GET'])
@role_required('instructor', 'admin')
def list_ascents():
    """Список всех восхождений. Только для instructor/admin."""
    ascents = Ascent.query.order_by(Ascent.ascent_date.desc()).all()
    
    return jsonify([{
        "id": a.id,
        "user_id": a.user_id,
        "username": a.user.username,
        "mountain_id": a.mountain_id,
        "mountain": a.mountain.name,
        "group_id": a.group_id,
        "group": a.group.name if a.group else None,
        "ascent_date": a.ascent_date.isoformat(),
        "is_successful": a.is_successful,
        "notes": a.notes
    } for a in ascents]), 200


@ascents_bp.route('/my', methods=['GET'])
@jwt_required()
def my_ascents():
    """Мои восхождения. Доступно любому аутентифицированному пользователю."""
    user_id = int(get_jwt_identity())
    ascents = Ascent.query.filter_by(user_id=user_id).order_by(Ascent.ascent_date.desc()).all()
    
    return jsonify([{
        "id": a.id,
        "mountain_id": a.mountain_id,
        "mountain": a.mountain.name,
        "mountain_height": a.mountain.height,
        "mountain_difficulty": a.mountain.difficulty_level,
        "group_id": a.group_id,
        "group": a.group.name if a.group else None,
        "ascent_date": a.ascent_date.isoformat(),
        "is_successful": a.is_successful,
        "notes": a.notes
    } for a in ascents]), 200


@ascents_bp.route('/<int:ascent_id>', methods=['GET'])
@jwt_required()
def get_ascent(ascent_id):
    """Информация об одном восхождении."""
    ascent = Ascent.query.get(ascent_id)
    if not ascent:
        return jsonify({"error": "Восхождение не найдено"}), 404
    
    return jsonify({
        "id": ascent.id,
        "user_id": ascent.user_id,
        "username": ascent.user.username,
        "mountain_id": ascent.mountain_id,
        "mountain": ascent.mountain.name,
        "group_id": ascent.group_id,
        "group": ascent.group.name if ascent.group else None,
        "ascent_date": ascent.ascent_date.isoformat(),
        "is_successful": ascent.is_successful,
        "notes": ascent.notes
    }), 200


@ascents_bp.route('', methods=['POST'])
@role_required('instructor', 'admin')
def create():
    """Создать восхождение. Только для instructor/admin."""
    schema = AscentSchema()
    
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    # Вызов сервиса - там все бизнес-правила
    success, message, ascent = create_ascent(
        user_id=data['user_id'],
        mountain_id=data['mountain_id'],
        group_id=data.get('group_id'),
        ascent_date=data['ascent_date'],
        is_successful=data.get('is_successful', False),
        notes=data.get('notes')
    )
    
    if not success:
        # 403 для бизнес-правил, 400 для прочих
        status = 403 if "уровень" in message or "Дата" in message else 400
        return jsonify({"error": message}), status
    
    return jsonify({
        "message": message,
        "ascent": {
            "id": ascent.id,
            "user_id": ascent.user_id,
            "mountain_id": ascent.mountain_id,
            "group_id": ascent.group_id,
            "ascent_date": ascent.ascent_date.isoformat(),
            "is_successful": ascent.is_successful
        }
    }), 201


@ascents_bp.route('/<int:ascent_id>', methods=['PUT'])
@role_required('instructor', 'admin')
def update(ascent_id):
    """Обновить восхождение."""
    ascent = Ascent.query.get(ascent_id)
    if not ascent:
        return jsonify({"error": "Восхождение не найдено"}), 404
    
    schema = AscentUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    # Если меняется дата или группа - валидируем
    new_date = data.get('ascent_date', ascent.ascent_date)
    new_group_id = data.get('group_id', ascent.group_id)
    
    dates_ok, dates_error = validate_ascent_dates(new_group_id, new_date)
    if not dates_ok:
        return jsonify({"error": dates_error}), 403
    
    for field in ['mountain_id', 'group_id', 'ascent_date', 'is_successful', 'notes']:
        if field in data:
            setattr(ascent, field, data[field])
    
    db.session.commit()
    
    return jsonify({"message": "Восхождение обновлено"}), 200


@ascents_bp.route('/<int:ascent_id>', methods=['DELETE'])
@role_required('admin')
def delete(ascent_id):
    """Удалить восхождение. Только для admin."""
    ascent = Ascent.query.get(ascent_id)
    if not ascent:
        return jsonify({"error": "Восхождение не найдено"}), 404
    
    db.session.delete(ascent)
    db.session.commit()
    
    return jsonify({"message": "Восхождение удалено"}), 200