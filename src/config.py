import os
from dotenv import load_dotenv

load_dotenv()


DISPATCH_JWT_SECRET: str = os.getenv("DISPATCH_JWT_SECRET", "default_secret")
SQLALCHEMY_DATABASE_URI: str = os.getenv(
    "SQLALCHEMY_DATABASE_URI", "sqlite+aiosqlite:///lingoplay.db"
)
