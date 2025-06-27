from pathlib import Path

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.errors import AlreadyExistsError
from src.repository import AlchemyRepository, S3Repository
from src.uploads.models import Games, Videos
from src.uploads.schemas import VideoCreate


class VideoRepository(AlchemyRepository):
    model = Videos
    _dir_name = "videos"

    def __init__(self, session: AsyncSession, s3_repository: S3Repository):
        super().__init__(session)
        self._s3_repository = s3_repository

    async def create_one(self, data: VideoCreate) -> Videos:
        path = f"{data.user_id}/{self._dir_name}/{data.title}{Path(data.file.filename).suffix}"

        if await self.exists(path=path):
            raise AlreadyExistsError(self.model.__tablename__, "path", path)

        url = await self._s3_repository.upload_file(data.file.file, path)

        async with self._session as session:
            result = await session.execute(select(Games).where(Games.id.in_(data.game_ids)))
            games = result.scalars().all()

            video = Videos(user_id=data.user_id, path=url, title=data.title, games=set(games))
            session.add(video)
            await session.commit()
            await session.refresh(video)
            return video

    async def exists(self, path: str):
        async with self._session as session:
            stmt = select(exists().where(Videos.path.like(f"%{path}")))
            result = await session.execute(stmt)
            return result.scalar()

