import secrets
import string

import bcrypt
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base


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
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str] = mapped_column(LargeBinary)

    token: Mapped["UserTokens"] = relationship(back_populates="user", uselist=False)  # noqa: F821

    def verify_password(self, password: str) -> bool:
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def set_password(self, password: str) -> None:
        if not password:
            raise ValueError("Password cannot be empty")
        self.password = hash_password(password)

    def __repr__(self):
        return f"LingoplayUser(id={self.id}, email='{self.email}', username='{self.username}')"
