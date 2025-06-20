import os

from dotenv import load_dotenv

load_dotenv()


DISPATCH_JWT_SECRET: str = os.getenv("DISPATCH_JWT_SECRET", "default_secret")
SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite+aiosqlite:///lingoplay.db")

JWT_SECRET_KEY: str = os.getenv("SECRET_KEY", "SECRET_KEY")
REFRESH_SECRET_KEY = os.getenv("SECRET_KEY_REFRESH", "SECRET_KEY_REFRESH")

JWT_ACCESS_TOKEN_EXPIRES_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 10)
JWT_REFRESH_TOKEN_EXPIRES_MINUTES = os.getenv("JWT_REFRESH_TOKEN_EXPIRES_MINUTES", 60)
