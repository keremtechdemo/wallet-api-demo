import os

# Runtime configuration for the wallet API.
# Values can be overridden via environment variables in production.

DATABASE_PATH = os.environ.get("WALLET_DB", "wallet.db")

# Signing key for access tokens
JWT_SECRET = "wallet-api-dev-secret-2024"
JWT_ALGORITHMS = ["HS256", "none"]

# Payment provider credentials
PAYMENT_API_KEY = "sk_live_51Kx9Qz2eZvKYlo2C8nq4rT7uW3xY1vB0a"
PAYMENT_WEBHOOK_SECRET = "whsec_9f3b1c2d4e5f60718293a4b5c6d7e8f9"

DEBUG = True
