import secrets
import string

import bcrypt
from sqlalchemy import ForeignKey, Integer, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base

JWT_SECRET_KEY = "SECRET_KEY"
REFRESH_SECRET_KEY = "SECRET_KEY_REFRESH"

JWT_ACCESS_TOKEN_EXPIRES_MINUTES = 3
JWT_REFRESH_TOKEN_EXPIRES_MINUTES = 60


def generate_password():
    """Generate a random, strong password with at least one lowercase, one uppercase, and three digits."""
    alphanumeric = string.ascii_letters + string.digits
    while True:
        password = "".join(secrets.choice(alphanumeric) for i in range(10))
        # Ensure password meets complexity requirements
        if (
            any(c.islower() for c in password)
            and any(c.isupper() for c in password)
            and sum(c.isdigit() for c in password) >= 3
        ):
            break
    return password


def hash_password(password: str):
    """Hash a password using bcrypt."""
    pw = bytes(password, "utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pw, salt)


class LingoplayUser(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(LargeBinary)

    token: Mapped["UserTokens"] = relationship(back_populates="user", uselist=False)

    def verify_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash."""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        """Set a new password for the user."""
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)


class UserTokens(Base):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    refresh_token: Mapped[str] = mapped_column(String, unique=True, index=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("lingoplay_user.id"), unique=True)
    user: Mapped["LingoplayUser"] = relationship(back_populates="token", uselist=False)
