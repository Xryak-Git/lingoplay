from pathlib import Path

from sqlalchemy import select

from src.database.core import new_session
from src.repository import AlchemyRepository, S3Repository
from src.videos.models import Games, Videos
from src.videos.schemas import VideoCreate


class VideoRepository(AlchemyRepository):
    model = Videos
    _dir_name = "videos"

    def __init__(self, s3_repository: S3Repository):
        self._s3_repository = s3_repository

    async def create_one(self, data: VideoCreate) -> Videos:
        path = await self._s3_repository.upload_file(
            data.file.file, f"{data.user_id}/{self._dir_name}/{data.title}{Path(data.file.filename).suffix}"
        )
        async with new_session() as session:
            result = await session.execute(
                select(Games).where(Games.id.in_(data.game_ids))
            )
            games = result.scalars().all()

            video = Videos(
                user_id=data.user_id,
                path=path,
                title=data.title,
                games=set(games)
            )
            session.add(video)
            await session.commit()
            await session.refresh(video)
            return video


