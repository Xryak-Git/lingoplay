from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.core import Base
from src.uploads.association_tables import videos_games_association
from src.users.models import LingoplayUser


class Games(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)

    videos: Mapped[set["Videos"]] = relationship(secondary=videos_games_association, back_populates="games")


class Videos(Base):

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True)
    path: Mapped[str] = mapped_column(unique=True)

    user_id: Mapped[int] = mapped_column(ForeignKey("lingoplay_user.id"))
    user: Mapped["LingoplayUser"] = relationship(back_populates="videos", uselist=False)

    games: Mapped[set["Games"]] = relationship(secondary=videos_games_association, back_populates="videos")

