from flask import Blueprint, request, jsonify, make_response, redirect
from ..db import get_conn, run_raw
from ..auth_utils import sha1, make_token
import random
import string

auth_bp = Blueprint("auth", __name__)

# VULN: mass assignment — "role" is accepted straight from the client and
# persisted, so POSTing {"role": "admin"} grants instant admin privileges.
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json or {}
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password, role, bio) VALUES (%s,%s,%s,%s,%s)",
            (data.get("username"), data.get("email"), sha1(data.get("password", "")),
             data.get("role", "user"), data.get("bio", ""))
        )
        conn.commit()
        return jsonify({"status": "registered"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400  # VULN: raw DB error leaked
    finally:
        cur.close(); conn.close()

# VULN: SQL injection — username is f-string'd directly into the query.
# e.g. username = "admin' -- " bypasses the password check entirely.
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "")
    password = sha1(data.get("password", ""))
    sql = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    try:
        rows = run_raw(sql)  # VULN: no rate limiting on this endpoint either
    except Exception as e:
        return jsonify({"error": str(e), "query": sql}), 500  # VULN: echoes injected query
    if not rows:
        return jsonify({"error": "Invalid credentials"}), 401
    user = rows[0]
    token = make_token(user)
    resp = make_response(jsonify({"token": token, "user": {"id": user["id"], "username": user["username"], "role": user["role"]}}))
    resp.set_cookie("token", token, httponly=False, secure=False, samesite=None)  # VULN: weak cookie flags
    return resp

# VULN: predictable password-reset token — short, low-entropy, generated with
# the non-cryptographic `random` module, and emailed nowhere (just returned
# in the API response for "convenience" in this lab build).
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json or {}
    username = data.get("username", "")
    token = "".join(random.choice(string.digits) for _ in range(4))  # VULN: 4-digit numeric token, 10000 possibilities
    run_raw(f"UPDATE users SET reset_token = '{token}' WHERE username = '{username}'")
    return jsonify({"reset_token": token})  # VULN: token should never be returned to the caller

@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    username = data.get("username", "")
    token = data.get("token", "")
    new_password = sha1(data.get("new_password", ""))
    rows = run_raw(f"SELECT * FROM users WHERE username = '{username}' AND reset_token = '{token}'")
    if not rows:
        return jsonify({"error": "Invalid token"}), 400
    run_raw(f"UPDATE users SET password = '{new_password}', reset_token = NULL WHERE username = '{username}'")
    return jsonify({"status": "password reset"})

# VULN: open redirect
@auth_bp.route("/post-login-redirect")
def post_login_redirect():
    dest = request.args.get("redirect", "/")
    return redirect(dest)
