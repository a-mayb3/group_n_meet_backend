import os

SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

BIND_ADDRESS = "0.0.0.0"
PORT = 8000
