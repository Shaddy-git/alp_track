from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models.group import Group
from models.user import User
from schemas.group import GroupSchema, AddMemberSchema
from services.ascent_service import add_climber_to_group
from utils.decorators import role_required

groups_bp = Blueprint('groups', __name__)


@groups_bp.route('', methods=['GET'])
@jwt_required()
def list_groups():
    """Список всех групп."""
    groups = Group.query.all()
    return jsonify([{
        "id": g.id,
        "name": g.name,
        "start_date": g.start_date.isoformat(),
        "end_date": g.end_date.isoformat(),
        "status": g.status,
        "leader_id": g.leader_id,
        "members_count": len(g.members)
    } for g in groups]), 200


@groups_bp.route('', methods=['POST'])
@role_required('instructor', 'admin')
def create_group():
    """Создать новую группу. Только для инструктора или администратора."""
    schema = GroupSchema()
    
    try:
        data = schema.load(request.get_json() or {})
        import sys
        print(f"DEBUG received name: {data.get('name')!r}", file=sys.stderr)
        print(f"DEBUG encoded: {data.get('name', '').encode('utf-8')}", file=sys.stderr)
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    # Проверка, что лидер существует
    leader = User.query.get(data['leader_id'])
    if not leader:
        return jsonify({"error": "Лидер не найден"}), 404
    
    if data['start_date'] > data['end_date']:
        return jsonify({"error": "Дата начала позже даты окончания"}), 400
    
    group = Group(
        name=data['name'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        leader_id=data['leader_id'],
        status=data.get('status', 'planning')
    )
    db.session.add(group)
    db.session.commit()
    
    return jsonify({"message": "Группа создана", "id": group.id}), 201


@groups_bp.route('/<int:group_id>/members', methods=['POST'])
@jwt_required()
def add_member(group_id):
    """Добавить участника в группу.
    
    Здесь работает бизнес-правило: уровень подготовки альпиниста
    должен быть не ниже сложности горы, на которую идёт группа.
    """
    schema = AddMemberSchema()
    
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    success, message = add_climber_to_group(data['user_id'], group_id)
    
    if not success:
        # 403 Forbidden - операция не разрешена бизнес-правилом
        return jsonify({"error": message}), 403
    
    return jsonify({"message": message}), 200