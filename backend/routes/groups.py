from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from extensions import db
from models.group import Group
from models.user import User
from models.ascent import Ascent
from schemas.group import GroupSchema, AddMemberSchema, GroupUpdateSchema
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

@groups_bp.route('/<int:group_id>', methods=['GET'])
@jwt_required()
def get_group(group_id):
    """Детали одной группы со списком участников."""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Группа не найдена"}), 404
    
    return jsonify({
        "id": group.id,
        "name": group.name,
        "start_date": group.start_date.isoformat(),
        "end_date": group.end_date.isoformat(),
        "status": group.status,
        "leader_id": group.leader_id,
        "leader": group.members and next((m.username for m in group.members if m.id == group.leader_id), None),
        "members": [{
            "id": m.id,
            "username": m.username,
            "full_name": m.full_name,
            "experience_level": m.experience_level,
            "role_in_group": next((gm[0] for gm in db.session.execute(
                db.text("SELECT role FROM group_members WHERE group_id=:g AND user_id=:u"),
                {"g": group_id, "u": m.id}
            ).fetchall()), 'member')
        } for m in group.members]
    }), 200


@groups_bp.route('/<int:group_id>', methods=['PUT'])
@role_required('instructor', 'admin')
def update_group(group_id):
    """Обновить группу. Только для instructor/admin."""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Группа не найдена"}), 404
    
    schema = GroupUpdateSchema()
    try:
        data = schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify({"error": "Ошибка валидации", "details": err.messages}), 400
    
    # Валидация: end_date не раньше start_date
    new_start = data.get('start_date', group.start_date)
    new_end = data.get('end_date', group.end_date)
    if new_start > new_end:
        return jsonify({"error": "Дата начала позже даты окончания"}), 400
    
    for field in ['name', 'start_date', 'end_date', 'status']:
        if field in data:
            setattr(group, field, data[field])
    
    db.session.commit()
    
    return jsonify({"message": "Группа обновлена"}), 200


@groups_bp.route('/<int:group_id>', methods=['DELETE'])
@role_required('admin')
def delete_group(group_id):
    """Удалить группу. Только для admin.
    
    Нельзя удалить группу, если у неё есть восхождения.
    """
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Группа не найдена"}), 404
    
    # Проверка: есть ли восхождения у группы
    ascents_count = Ascent.query.filter_by(group_id=group_id).count()
    if ascents_count > 0:
        return jsonify({
            "error": f"Нельзя удалить группу: с ней связано {ascents_count} восхождений"
        }), 409
    
    # Удаляем связи M:N
    group.members.clear()
    db.session.delete(group)
    db.session.commit()
    
    return jsonify({"message": "Группа удалена"}), 200


@groups_bp.route('/<int:group_id>/members/<int:user_id>', methods=['DELETE'])
@role_required('instructor', 'admin')
def remove_member(group_id, user_id):
    """Исключить участника из группы. Только для instructor/admin."""
    group = Group.query.get(group_id)
    if not group:
        return jsonify({"error": "Группа не найдена"}), 404
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    # Проверка: пользователь в группе?
    if user not in group.members:
        return jsonify({"error": "Пользователь не состоит в этой группе"}), 400
    
    # Нельзя исключить лидера группы
    if user.id == group.leader_id:
        return jsonify({"error": "Нельзя исключить лидера группы"}), 403
    
    group.members.remove(user)
    db.session.commit()
    
    return jsonify({"message": "Участник исключён из группы"}), 200


@groups_bp.route('/<int:group_id>/join', methods=['POST'])
@jwt_required()
def join_group(group_id):
    """Присоединиться к группе.
    
    Пользователь сам себя добавляет. Применяется бизнес-правило:
    уровень подготовки должен быть не ниже сложности горы группы.
    """
    user_id = int(get_jwt_identity())
    
    success, message = add_climber_to_group(user_id, group_id)
    
    if not success:
        return jsonify({"error": message}), 403
    
    return jsonify({"message": message}), 200