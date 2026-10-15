from datetime import date
from flask import Blueprint, request, jsonify
from sqlalchemy import func

from extensions import db
from models.ascent import Ascent
from models.mountain import Mountain
from models.user import User
from utils.decorators import role_required

reports_bp = Blueprint('reports', __name__)


@reports_bp.route('/climbers-by-mountain/<int:mountain_id>', methods=['GET'])
@role_required('instructor', 'admin')
def climbers_by_mountain(mountain_id):
    """Отчёт: список альпинистов, покоривших указанную гору.
    
    Возвращает только успешные восхождения.
    """
    mountain = Mountain.query.get(mountain_id)
    if not mountain:
        return jsonify({"error": "Гора не найдена"}), 404
    
    # Находим успешные восхождения на эту гору
    ascents = (Ascent.query
               .filter_by(mountain_id=mountain_id, is_successful=True)
               .join(User)
               .order_by(Ascent.ascent_date.desc())
               .all())
    
    # Уникальные альпинисты (могли ходить несколько раз)
    seen_users = set()
    climbers = []
    for a in ascents:
        if a.user_id not in seen_users:
            seen_users.add(a.user_id)
            climbers.append({
                "user_id": a.user_id,
                "username": a.user.username,
                "full_name": a.user.full_name,
                "experience_level": a.user.experience_level,
                "first_ascent_date": a.ascent_date.isoformat()
            })
    
    return jsonify({
        "mountain": {
            "id": mountain.id,
            "name": mountain.name,
            "height": mountain.height,
            "difficulty_level": mountain.difficulty_level
        },
        "total_ascents": len(ascents),
        "unique_climbers": len(climbers),
        "climbers": climbers
    }), 200


@reports_bp.route('/successful-ascents', methods=['GET'])
@role_required('instructor', 'admin')
def successful_ascents():
    """Отчёт: количество успешных восхождений за год.
    
    Query-параметры:
        year: int (опционально, по умолчанию - текущий год)
    """
    year = request.args.get('year', type=int, default=date.today().year)
    
    start_date = date(year, 1, 1)
    end_date = date(year, 12, 31)
    
    total = Ascent.query.filter(
        Ascent.ascent_date >= start_date,
        Ascent.ascent_date <= end_date
    ).count()
    
    successful = Ascent.query.filter(
        Ascent.ascent_date >= start_date,
        Ascent.ascent_date <= end_date,
        Ascent.is_successful == True  # noqa: E712
    ).count()
    
    return jsonify({
        "year": year,
        "total_ascents": total,
        "successful_ascents": successful,
        "failed_ascents": total - successful,
        "success_rate": round(successful / total * 100, 2) if total > 0 else 0
    }), 200


@reports_bp.route('/popular-mountains', methods=['GET'])
@role_required('instructor', 'admin')
def popular_mountains():
    """Отчёт: топ гор по числу восхождений.
    
    Query-параметры:
        limit: int (по умолчанию 5)
    """
    limit = request.args.get('limit', type=int, default=5)
    
    results = (db.session.query(
                    Mountain.id,
                    Mountain.name,
                    Mountain.height,
                    Mountain.difficulty_level,
                    func.count(Ascent.id).label('ascents_count')
                )
                .join(Ascent, Ascent.mountain_id == Mountain.id)
                .group_by(Mountain.id)
                .order_by(func.count(Ascent.id).desc())
                .limit(limit)
                .all())
    
    return jsonify([{
        "mountain_id": r.id,
        "name": r.name,
        "height": r.height,
        "difficulty_level": r.difficulty_level,
        "ascents_count": r.ascents_count
    } for r in results]), 200


@reports_bp.route('/user-stats/<int:user_id>', methods=['GET'])
@role_required('instructor', 'admin')
def user_stats(user_id):
    """Отчёт: статистика пользователя по восхождениям."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Пользователь не найден"}), 404
    
    total = Ascent.query.filter_by(user_id=user_id).count()
    successful = Ascent.query.filter_by(user_id=user_id, is_successful=True).count()
    
    # Уникальные горы
    unique_mountains = (db.session.query(func.count(func.distinct(Ascent.mountain_id)))
                        .filter_by(user_id=user_id)
                        .scalar())
    
    # Самая высокая покорённая гора
    highest = (db.session.query(Mountain)
               .join(Ascent, Ascent.mountain_id == Mountain.id)
               .filter(Ascent.user_id == user_id, Ascent.is_successful == True)  # noqa: E712
               .order_by(Mountain.height.desc())
               .first())
    
    return jsonify({
        "user": {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "experience_level": user.experience_level
        },
        "total_ascents": total,
        "successful_ascents": successful,
        "unique_mountains": unique_mountains or 0,
        "highest_mountain": {
            "name": highest.name,
            "height": highest.height
        } if highest else None
    }), 200