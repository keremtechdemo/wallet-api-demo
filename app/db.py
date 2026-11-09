import hashlib
import sqlite3

from . import config


def get_conn():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS wallets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    currency TEXT NOT NULL,
    balance_cents INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wallet_id INTEGER NOT NULL,
    amount_cents INTEGER NOT NULL,
    merchant TEXT NOT NULL,
    note TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (wallet_id) REFERENCES wallets(id)
);
"""

SEED_USERS = [
    ("alice@example.com", "alice123", "user"),
    ("bob@example.com", "bob123", "user"),
    ("admin@example.com", "admin123", "admin"),
]

SEED_TRANSACTIONS = [
    (1, -1299, "Coffee Roasters", "latte"),
    (1, -4500, "Grocery Mart", None),
    (1, 250000, "Payroll Inc", "salary"),
    (2, -8999, "Gadget Store", "headphones"),
    (2, -1500, "Coffee Roasters", None),
    (3, -120000, "Rent Co", "november"),
]


def init_db():
    conn = get_conn()
    conn.executescript(SCHEMA)
    existing = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if existing == 0:
        for email, password, role in SEED_USERS:
            conn.execute(
                "INSERT INTO users (email, password_hash, role) VALUES (?, ?, ?)",
                (email, hash_password(password), role),
            )
        conn.execute("INSERT INTO wallets (user_id, currency, balance_cents) VALUES (1, 'USD', 244201)")
        conn.execute("INSERT INTO wallets (user_id, currency, balance_cents) VALUES (2, 'USD', 89501)")
        conn.execute("INSERT INTO wallets (user_id, currency, balance_cents) VALUES (3, 'USD', 1500000)")
        for wallet_id, amount, merchant, note in SEED_TRANSACTIONS:
            conn.execute(
                "INSERT INTO transactions (wallet_id, amount_cents, merchant, note) VALUES (?, ?, ?, ?)",
                (wallet_id, amount, merchant, note),
            )
        conn.commit()
    conn.close()
