from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from extensions import db
from models.mountain import Mountain
from models.ascent import Ascent
from schemas.mountain import MountainSchema
from utils.decorators import role_required

mountains_bp = Blueprint('mountains', __name__)


@mountains_bp.route('', methods=['GET'])
@jwt_required()
def list_mountains():
    """Список всех гор с фильтрами."""
    query = Mountain.query
    
    min_height = request.args.get('min_height', type=int)
    if min_height:
        query = query.filter(Mountain.height >= min_height)
    
    max_difficulty = request.args.get('max_difficulty', type=int)
    if max_difficulty:
        query = query.filter(Mountain.difficulty_level <= max_difficulty)
    
    mountains = query.order_by(Mountain.height.desc()).all()
    
    return jsonify([{
        "id": m.id,
        "name": m.name,
        "height": m.height,
        "country": m.country,
        "difficulty_level": m.difficulty_level
    } for m in mountains]), 200


@mountains_bp.route('/<int:mountain_id>', methods=['GET'])
@jwt_required()
def get_mountain(mountain_id):
    """Информация об одной горе."""
    mountain = Mountain.query.get(mountain_id)
    if not mountain:
        return jsonify({"error": "Гора не найдена"}), 404
    
    return jsonify({
        "id": mountain.id,
        "name": mountain.name,
        "height": mountain.height,
        "country": mountain.country,
        "difficulty_level": mountain.difficulty_level
    }), 200


@mountains_bp.route('', methods=['POST'])
@role_required('admin')
def create_mountain():
    """Создать новую гору. Только для admin."""
    schema = MountainSchema()
    
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    if Mountain.query.filter_by(name=data['name']).first():
        return jsonify({"error": "Гора с таким названием уже существует"}), 409
    
    mountain = Mountain(
        name=data['name'],
        height=data['height'],
        country=data['country'],
        difficulty_level=data['difficulty_level']
    )
    
    db.session.add(mountain)
    db.session.commit()
    
    return jsonify({
        "message": "Гора добавлена",
        "mountain": {
            "id": mountain.id,
            "name": mountain.name,
            "height": mountain.height,
            "country": mountain.country,
            "difficulty_level": mountain.difficulty_level
        }
    }), 201


@mountains_bp.route('/<int:mountain_id>', methods=['PUT'])
@role_required('admin')
def update_mountain(mountain_id):
    """Обновить гору. Только для admin."""
    mountain = Mountain.query.get(mountain_id)
    if not mountain:
        return jsonify({"error": "Гора не найдена"}), 404
    
    schema = MountainSchema()
    
    try:
        data = schema.load(request.get_json() or {}, partial=True)
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    if 'name' in data and data['name'] != mountain.name:
        if Mountain.query.filter_by(name=data['name']).first():
            return jsonify({"error": "Гора с таким названием уже существует"}), 409
    
    for field in ['name', 'height', 'country', 'difficulty_level']:
        if field in data:
            setattr(mountain, field, data[field])
    
    db.session.commit()
    
    return jsonify({"message": "Гора обновлена"}), 200


@mountains_bp.route('/<int:mountain_id>', methods=['DELETE'])
@role_required('admin')
def delete_mountain(mountain_id):
    """Удалить гору. Только для admin.
    
    Если на гору есть восхождения - удаление запрещено.
    """
    mountain = Mountain.query.get(mountain_id)
    if not mountain:
        return jsonify({"error": "Гора не найдена"}), 404
    
    ascents_count = Ascent.query.filter_by(mountain_id=mountain_id).count()
    if ascents_count > 0:
        return jsonify({
            "error": f"Нельзя удалить гору: на неё записано {ascents_count} восхождений"
        }), 409
    
    db.session.delete(mountain)
    db.session.commit()
    
    return jsonify({"message": "Гора удалена"}), 200