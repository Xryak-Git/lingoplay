from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base
from src.users.models import LingoplayUser


class Games(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column()

    videos: Mapped[list["Videos"]] = relationship(back_populates="game")


class Videos(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    path: Mapped[str] = mapped_column(unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("lingoplay_user.id"))
    user: Mapped["LingoplayUser"] = relationship(back_populates="videos")

    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"))
    game: Mapped[Games] = relationship(back_populates="videos")
