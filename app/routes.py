from flask import Blueprint, g, jsonify, request

from .auth import authenticate, issue_token, login_required
from .db import get_conn

api = Blueprint("api", __name__, url_prefix="/api")


@api.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    user = authenticate(body.get("email", ""), body.get("password", ""))
    if not user:
        return jsonify({"error": "invalid credentials"}), 401
    return jsonify({"token": issue_token(user["id"], user["role"])})


@api.get("/me")
@login_required
def me():
    conn = get_conn()
    user = conn.execute("SELECT id, email, role FROM users WHERE id = ?", (g.user_id,)).fetchone()
    conn.close()
    return jsonify(dict(user))


@api.get("/wallets/<int:wallet_id>")
@login_required
def get_wallet(wallet_id: int):
    conn = get_conn()
    wallet = conn.execute(
        "SELECT id, user_id, currency, balance_cents FROM wallets WHERE id = ?",
        (wallet_id,),
    ).fetchone()
    conn.close()
    if not wallet:
        return jsonify({"error": "not found"}), 404
    return jsonify(dict(wallet))


@api.get("/wallets/<int:wallet_id>/transactions")
@login_required
def list_transactions(wallet_id: int):
    q = request.args.get("q", "")
    sort = request.args.get("sort", "created_at")
    sort_columns = {
        "id": "id",
        "amount_cents": "amount_cents",
        "merchant": "merchant",
        "note": "note",
        "created_at": "created_at",
    }
    if sort not in sort_columns:
        return jsonify({"error": "invalid sort"}), 400
    sql = (
        "SELECT id, amount_cents, merchant, note, created_at FROM transactions "
        f"WHERE wallet_id = ? AND merchant LIKE ? ORDER BY {sort_columns[sort]} DESC"
    )
    conn = get_conn()
    rows = conn.execute(sql, (wallet_id, f"%{q}%")).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@api.post("/wallets/<int:wallet_id>/transfer")
@login_required
def transfer(wallet_id: int):
    body = request.get_json(silent=True) or {}
    to_wallet = int(body.get("to_wallet", 0))
    amount = int(body.get("amount_cents", 0))
    conn = get_conn()
    conn.execute("UPDATE wallets SET balance_cents = balance_cents - ? WHERE id = ?", (amount, wallet_id))
    conn.execute("UPDATE wallets SET balance_cents = balance_cents + ? WHERE id = ?", (amount, to_wallet))
    conn.execute(
        "INSERT INTO transactions (wallet_id, amount_cents, merchant, note) VALUES (?, ?, 'Transfer', ?)",
        (wallet_id, -amount, f"to wallet {to_wallet}"),
    )
    conn.commit()
    conn.close()
    return jsonify({"status": "ok"})


@api.get("/admin/users")
def admin_users():
    if request.headers.get("X-Admin") != "true":
        return jsonify({"error": "forbidden"}), 403
    conn = get_conn()
    rows = conn.execute("SELECT id, email, role, password_hash FROM users").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])
