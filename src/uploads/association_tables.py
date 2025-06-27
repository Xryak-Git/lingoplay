from sqlalchemy import Column, ForeignKey, Table

from src.database.core import Base

videos_games_association = Table(
    "videos_games_association",
    Base.metadata,
    Column("video_id", ForeignKey("videos.id", ondelete="CASCADE"), primary_key=True),
    Column("game_id", ForeignKey("games.id", ondelete="CASCADE"), primary_key=True),
)
