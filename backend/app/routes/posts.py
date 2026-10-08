from flask import Blueprint, request, jsonify
from ..db import get_conn, run_raw
from ..auth_utils import require_auth, require_admin

posts_bp = Blueprint("posts", __name__)

@posts_bp.route("/")
def list_posts():
    rows = run_raw("SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id ORDER BY posts.id DESC")
    return jsonify(rows)

@posts_bp.route("/<int:post_id>")
def get_post(post_id):
    rows = run_raw(f"SELECT posts.*, users.username FROM posts JOIN users ON posts.user_id = users.id WHERE posts.id = {post_id}")
    if not rows:
        return jsonify({"error": "Not found"}), 404
    return jsonify(rows[0])

# VULN: SQL injection — raw, unparameterized LIKE query built via f-string.
# e.g. /api/posts/search?q=x' UNION SELECT id,username,password,role,... FROM users --
@posts_bp.route("/search")
def search_posts():
    q = request.args.get("q", "")
    sql = f"SELECT * FROM posts WHERE title LIKE '%{q}%' OR body LIKE '%{q}%'"
    try:
        rows = run_raw(sql)
    except Exception as e:
        return jsonify({"error": str(e), "query": sql}), 500
    # VULN: raw query string reflected back for the frontend's results banner,
    # which renders it as HTML -> reflected XSS.
    return jsonify({"query": q, "results": rows})

@posts_bp.route("/", methods=["POST"])
@require_auth
def create_post():
    data = request.json or {}
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO posts (user_id, title, body) VALUES (%s,%s,%s)",
                (request.user["id"], data.get("title"), data.get("body")))
    conn.commit()
    pid = cur.lastrowid
    cur.close(); conn.close()
    return jsonify({"id": pid})

# VULN: broken access control — only requires login, not ownership or admin,
# so any authenticated user can delete anyone else's post.
@posts_bp.route("/<int:post_id>", methods=["DELETE"])
@require_auth
def delete_post(post_id):
    run_raw(f"DELETE FROM posts WHERE id = {post_id}")
    return jsonify({"status": "deleted"})
