from flask import Blueprint, request, jsonify
from ..db import get_conn, run_raw
from ..auth_utils import require_auth

comments_bp = Blueprint("comments", __name__)

@comments_bp.route("/<int:post_id>")
def list_comments(post_id):
    rows = run_raw(f"SELECT comments.*, users.username FROM comments JOIN users ON comments.user_id = users.id WHERE post_id = {post_id} ORDER BY comments.id DESC")
    return jsonify(rows)

# VULN: comment body stored with zero sanitization and rendered with v-html
# on the frontend -> stored XSS, same pattern as VulnMart's reviews but here
# it also runs on the *post author's own view*, so it can target privileged users.
@comments_bp.route("/<int:post_id>", methods=["POST"])
@require_auth
def add_comment(post_id):
    data = request.json or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO comments (post_id, user_id, body) VALUES (%s,%s,%s)",
                (post_id, request.user["id"], data.get("body")))
    conn.commit()
    cur.close(); conn.close()
    return jsonify({"status": "added"})
