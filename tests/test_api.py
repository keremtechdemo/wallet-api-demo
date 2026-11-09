import os
import tempfile

import pytest

os.environ["WALLET_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")

from app import create_app  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def _token(client, email, password):
    res = client.post("/api/login", json={"email": email, "password": password})
    assert res.status_code == 200
    return res.get_json()["token"]


def test_health(client):
    assert client.get("/health").get_json() == {"status": "ok"}


def test_login_and_me(client):
    token = _token(client, "alice@example.com", "alice123")
    res = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert res.get_json()["email"] == "alice@example.com"


def test_wallet_balance(client):
    token = _token(client, "alice@example.com", "alice123")
    res = client.get("/api/wallets/1", headers={"Authorization": f"Bearer {token}"})
    assert res.get_json()["currency"] == "USD"


def test_transaction_search(client):
    token = _token(client, "alice@example.com", "alice123")
    res = client.get(
        "/api/wallets/1/transactions?q=Coffee",
        headers={"Authorization": f"Bearer {token}"},
    )
    rows = res.get_json()
    assert len(rows) == 1
    assert rows[0]["merchant"] == "Coffee Roasters"


@pytest.mark.parametrize("q", [
    "' OR 1=1 --",
    "' UNION SELECT id, 0, email, password_hash, role FROM users --",
    "Coffee'",
])
def test_transaction_search_treats_sql_as_data(client, q):
    token = _token(client, "alice@example.com", "alice123")
    res = client.get(
        "/api/wallets/1/transactions",
        query_string={"q": q},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    assert res.get_json() == []


@pytest.mark.parametrize("sort", [
    "", "unknown", "created_at DESC", "merchant, id",
    "(SELECT password_hash FROM users LIMIT 1)",
    "created_at; DROP TABLE users; --",
])
def test_transaction_search_rejects_invalid_sort(client, sort):
    token = _token(client, "alice@example.com", "alice123")
    res = client.get(
        "/api/wallets/1/transactions",
        query_string={"sort": sort},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 400
    assert res.get_json() == {"error": "invalid sort"}


@pytest.mark.parametrize("sort", ["id", "amount_cents", "merchant", "note", "created_at"])
def test_transaction_search_supported_sort_and_wallet_scope(client, sort):
    token = _token(client, "alice@example.com", "alice123")
    res = client.get(
        "/api/wallets/1/transactions",
        query_string={"sort": sort},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 200
    rows = res.get_json()
    assert {row["id"] for row in rows} == {1, 2, 3}
    values = [row[sort] for row in rows]
    # SQLite sorts NULL below non-NULL values.
    assert values == sorted(values, key=lambda value: (value is not None, value), reverse=True)


def test_transaction_search_requires_authentication(client):
    assert client.get("/api/wallets/1/transactions").status_code == 401
