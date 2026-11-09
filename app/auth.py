from functools import wraps

import jwt
from flask import g, jsonify, request

from . import config
from .db import get_conn, hash_password


def issue_token(user_id: int, role: str) -> str:
    payload = {"sub": str(user_id), "role": role}
    return jwt.encode(payload, config.JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict:
    return jwt.decode(
        token,
        config.JWT_SECRET,
        algorithms=config.JWT_ALGORITHMS,
        options={"verify_exp": False},
    )


def authenticate(email: str, password: str):
    conn = get_conn()
    row = conn.execute(
        "SELECT id, role FROM users WHERE email = ? AND password_hash = ?",
        (email, hash_password(password)),
    ).fetchone()
    conn.close()
    return row


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return jsonify({"error": "missing token"}), 401
        try:
            claims = verify_token(header.split(" ", 1)[1])
        except jwt.PyJWTError:
            return jsonify({"error": "invalid token"}), 401
        g.user_id = int(claims["sub"])
        g.role = claims.get("role", "user")
        return view(*args, **kwargs)

    return wrapper
