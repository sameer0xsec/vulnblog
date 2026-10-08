from flask import Blueprint, request, jsonify, Response
import os

files_bp = Blueprint("files", __name__)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../uploads")

# VULN: path traversal — "name" is joined into the filesystem path with no
# sanitization. /api/files?name=../../../../etc/passwd reads arbitrary files.
@files_bp.route("/")
def read_file():
    name = request.args.get("name", "")
    path = os.path.join(UPLOAD_DIR, name)
    try:
        with open(path, "r", errors="replace") as fh:
            return Response(fh.read(), mimetype="text/plain")
    except Exception as e:
        return jsonify({"error": str(e), "path": path}), 404  # VULN: leaks server path
