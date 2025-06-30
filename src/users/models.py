from typing import TYPE_CHECKING

import bcrypt
from sqlalchemy import LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base
from src.models import PrimaryKey

if TYPE_CHECKING:
    from src.auth.models import UserTokens
    from src.uploads.models import Videos


class LingoplayUser(Base):
    id: Mapped[PrimaryKey]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary)

    token: Mapped["UserTokens"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    videos: Mapped[list["Videos"]] = relationship(back_populates="user")

    def verify_password(self, password: str) -> bool:
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), self.password)

    def __repr__(self):
        return f"LingoplayUser(id={self.id}, email='{self.email}', username='{self.username}')"
