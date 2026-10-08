import jwt
import hashlib
import os
from functools import wraps
from flask import request, jsonify, current_app

def sha1(s):
    # VULN: weak, unsalted hashing algorithm for passwords.
    return hashlib.sha1(s.encode()).hexdigest()

def make_token(user):
    secret = os.environ.get("SECRET_KEY", "changeme")
    # VULN: no expiration claim ("exp") set -> tokens never expire and can't
    # be invalidated short of rotating the secret for everyone.
    return jwt.encode({"id": user["id"], "username": user["username"], "role": user["role"]}, secret, algorithm="HS256")

def decode_token(token):
    secret = os.environ.get("SECRET_KEY", "changeme")
    # VULN: accepts both HS256 and "none" — a token with alg:none and no
    # signature is treated as valid.
    return jwt.decode(token, secret, algorithms=["HS256", "none"])

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else request.cookies.get("token")
        if not token:
            return jsonify({"error": "No token"}), 401
        try:
            request.user = decode_token(token)
        except Exception as e:
            # VULN: leaks internal exception detail to the client
            return jsonify({"error": "Invalid token", "detail": str(e)}), 401
        return f(*args, **kwargs)
    return wrapper

def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # VULN: trusts the role claim embedded in the client-supplied JWT,
        # which a user can set themselves at registration (mass assignment).
        if getattr(request, "user", {}).get("role") != "admin":
            return jsonify({"error": "Admin required"}), 403
        return f(*args, **kwargs)
    return wrapper
