import bcrypt
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base


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

    def __repr__(self):
        return f"LingoplayUser(id={self.id}, email='{self.email}', username='{self.username}')"
