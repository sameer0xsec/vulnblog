from flask import Blueprint, request, jsonify
from ..auth_utils import require_auth
import os

upload_bp = Blueprint("upload", __name__)
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "../../uploads")

# VULN: filename taken verbatim from the client, no extension allow-list,
# no content-type check -> arbitrary file upload. A .html/.svg file becomes
# stored XSS when visited directly; a path-traversal filename like
# "../../app/run.py" attempts to overwrite server source.
@upload_bp.route("/avatar", methods=["POST"])
@require_auth
def upload_avatar():
    f = request.files["file"]
    dest = os.path.join(UPLOAD_DIR, f.filename)
    f.save(dest)
    return jsonify({"url": f"/uploads/{f.filename}"})
