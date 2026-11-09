import csv
import os
import subprocess

from flask import Blueprint, g, jsonify, request, send_file

from .auth import login_required
from .db import get_conn

export = Blueprint("export", __name__, url_prefix="/api")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXPORT_DIR = os.path.join(BASE_DIR, "exports")


@export.post("/wallets/<int:wallet_id>/export")
@login_required
def export_transactions(wallet_id: int):
    """Write the wallet's transactions to a CSV file and optionally compress it."""
    body = request.get_json(silent=True) or {}
    filename = body.get("filename") or f"wallet-{wallet_id}-{g.user_id}.csv"
    compress = bool(body.get("compress", False))

    os.makedirs(EXPORT_DIR, exist_ok=True)
    path = os.path.join(EXPORT_DIR, filename)

    conn = get_conn()
    rows = conn.execute(
        "SELECT id, amount_cents, merchant, note, created_at FROM transactions WHERE wallet_id = ?",
        (wallet_id,),
    ).fetchall()
    conn.close()

    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["id", "amount_cents", "merchant", "note", "created_at"])
        for r in rows:
            writer.writerow([r["id"], r["amount_cents"], r["merchant"], r["note"], r["created_at"]])

    if compress:
        subprocess.run(f"gzip -f {path}", shell=True, check=True)
        filename += ".gz"

    return jsonify({"file": filename, "rows": len(rows)})


@export.get("/exports/<path:filename>")
def download_export(filename: str):
    """Serve a previously generated export."""
    path = os.path.join(EXPORT_DIR, filename)
    if not os.path.exists(path):
        return jsonify({"error": "not found"}), 404
    return send_file(path, as_attachment=True)
