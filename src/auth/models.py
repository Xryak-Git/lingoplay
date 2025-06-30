from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base

if TYPE_CHECKING:
    from src.users.models import LingoplayUsers


class UserTokens(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    refresh_token: Mapped[str] = mapped_column(unique=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("lingoplay_users.id", ondelete="CASCADE"),
        unique=True,
    )
    user: Mapped["LingoplayUsers"] = relationship(back_populates="token", uselist=False)
