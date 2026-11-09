# wallet-api-demo

A small Flask wallet / transactions API used as a **demo target for code security tooling**.

It is intentionally simple and intentionally imperfect. It exists so that automated
security review can be shown on a realistic, self-contained codebase.

**Do not deploy this anywhere reachable from the internet.**

## Run locally

```bash
pip install -r requirements.txt
python run.py
```

Seeded accounts: `alice@example.com / alice123`, `bob@example.com / bob123`, `admin@example.com / admin123`.

## Endpoints

| Method | Path | Description |
| --- | --- | --- |
| POST | `/api/login` | Returns a bearer token |
| GET | `/api/me` | Current user |
| GET | `/api/wallets/<id>` | Wallet balance |
| GET | `/api/wallets/<id>/transactions?q=&sort=` | Transaction search |
| POST | `/api/wallets/<id>/transfer` | Move funds between wallets |
| GET | `/api/admin/users` | Admin user listing |

## Tests

```bash
python -m pytest -q
```
