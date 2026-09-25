import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "nexira-dev-secret-change-in-production")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = False

    frontend_urls = [
        value.strip()
        for value in os.getenv("FRONTEND_URL", "http://localhost:5173,http://localhost:5174").split(",")
        if value.strip()
    ]
    if not frontend_urls:
        frontend_urls = ["http://localhost:5173", "http://localhost:5174"]

    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        allow_headers=["Content-Type", "Authorization", "Accept"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        supports_credentials=True,
    )
    JWTManager(app)

    from app.routes.auth import auth_bp
    from app.routes.projects import projects_bp
    from app.routes.workflow import workflow_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(projects_bp, url_prefix="/api/projects")
    app.register_blueprint(workflow_bp, url_prefix="/api/projects")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "app": "NEXIRA"})

    from app.db.connection import init_default_admin
    with app.app_context():
        try:
            init_default_admin()
        except Exception as e:
            print(f"[NEXIRA] Warning: Could not initialize default admin: {e}")

    return app
