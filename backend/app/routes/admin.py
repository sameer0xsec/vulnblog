from flask import Blueprint, request, jsonify
from ..db import run_raw
from ..auth_utils import require_auth, require_admin

admin_bp = Blueprint("admin", __name__)

# VULN: returns password hashes and reset tokens for every user.
@admin_bp.route("/users")
@require_auth
@require_admin
def list_users():
    rows = run_raw("SELECT * FROM users")
    return jsonify(rows)

# VULN: broken access control — missing @require_admin, so any logged-in
# user can PATCH any user's role (including their own) to "admin".
@admin_bp.route("/users/<int:user_id>", methods=["PATCH"])
@require_auth
def update_user(user_id):
    data = request.json or {}
    role = data.get("role")
    bio = data.get("bio")
    run_raw(f"UPDATE users SET role = '{role}', bio = '{bio}' WHERE id = {user_id}")
    return jsonify({"status": "updated"})
