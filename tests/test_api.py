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
