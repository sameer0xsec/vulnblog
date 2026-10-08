from flask import Flask, send_from_directory
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    # VULN: weak, hardcoded-fallback secret key signs session cookies — an
    # attacker who knows/brute-forces it can forge arbitrary Flask sessions.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "changeme")
    app.config["DEBUG"] = True  # VULN: debug mode in all environments, see run.py

    # VULN: wildcard CORS with credentials — any origin can make authenticated
    # cookie-based requests against this API.
    CORS(app, supports_credentials=True, origins="*")

    from .routes.auth import auth_bp
    from .routes.posts import posts_bp
    from .routes.comments import comments_bp
    from .routes.admin import admin_bp
    from .routes.upload import upload_bp
    from .routes.files import files_bp
    from .routes.tools import tools_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(posts_bp, url_prefix="/api/posts")
    app.register_blueprint(comments_bp, url_prefix="/api/comments")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(upload_bp, url_prefix="/api/upload")
    app.register_blueprint(files_bp, url_prefix="/api/files")
    app.register_blueprint(tools_bp, url_prefix="/api/tools")

    # VULN: uploaded files served with no access control and no
    # Content-Disposition, so uploaded HTML/SVG/JS executes in-browser.
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(os.path.join(os.path.dirname(__file__), "../uploads"), filename)

    return app
