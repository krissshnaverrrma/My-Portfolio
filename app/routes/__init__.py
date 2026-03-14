from .routes import main_bp, admin_bp


def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
