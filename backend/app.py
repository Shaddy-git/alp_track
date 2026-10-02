# backend/app.py
from flask import Flask, jsonify
from config import Config
from extensions import db, migrate, jwt


def create_app(config_class=Config):
    """Фабрика приложения (Application Factory pattern)."""
    
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Инициализация расширений
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Импорт моделей — ВАЖНО до миграций!
    from models import user, mountain, group, ascent  # noqa: F401
    
    # Регистрация blueprints (маршрутов)
    # Пока закомментируем — routes появятся в блоке 3
    # from routes.auth import auth_bp
    # app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    # Health-check (пункт 6 задания)
    @app.route('/health')
    def health():
        try:
            db.session.execute(db.text('SELECT 1'))
            return jsonify({
                "status": "ok",
                "database": "connected"
            }), 200
        except Exception:
            return jsonify({
                "status": "error",
                "database": "disconnected"
            }), 500
    
    # Глобальные обработчики ошибок (защита от утечки стек-трейсов)
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Ресурс не найден"}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Внутренняя ошибка сервера"}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)