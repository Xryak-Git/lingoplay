from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base
from src.models import PrimaryKey

if TYPE_CHECKING:
    from src.users.models import LingoplayUsers


class Games(Base):
    id: Mapped[PrimaryKey]
    title: Mapped[str] = mapped_column()

    videos: Mapped[list["Videos"]] = relationship(back_populates="game")
    users: Mapped[list["LingoplayUsers"]] = relationship(back_populates="games", secondary="lingoplay_users_games")


class LingoplayUsersGames(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("lingoplay_users.id", ondelete="CASCADE"), primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="CASCADE"), primary_key=True)


class Videos(Base):
    id: Mapped[PrimaryKey]
    title: Mapped[str] = mapped_column(index=True)
    path: Mapped[str] = mapped_column(unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("lingoplay_users.id", ondelete="CASCADE"), nullable=False)
    user: Mapped["LingoplayUsers"] = relationship(back_populates="videos")

    game_id: Mapped[int | None] = mapped_column(ForeignKey("games.id", ondelete="SET NULL"))
    game: Mapped[Games] = relationship(back_populates="videos")
