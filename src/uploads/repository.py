from pathlib import Path

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.errors import AlreadyExistsError
from src.repository import AlchemyRepository
from src.s3 import AbstractS3Repository
from src.uploads.models import Games, Videos
from src.uploads.schemas import GameCreate, VideoCreate
from src.users.models import LingoplayUsers


class VideoRepository(AlchemyRepository):
    model = Videos
    _dir_name = "videos"

    def __init__(self, session: AsyncSession, s3_repository: AbstractS3Repository):
        super().__init__(session)
        self._s3_repository = s3_repository

    async def create_one(self, data: VideoCreate) -> Videos:
        dir_path = self._build_dir_path(data.user_id, data.title)
        video_path = self._build_video_path(dir_path, data.video.filename)
        thumbnail_path = f"{dir_path}/thumbnail.png"

        if await self.exists(path=video_path):
            raise AlreadyExistsError(self.model.__tablename__, "path", video_path)

        video_url = await self._s3_repository.upload_file(data.video.file, video_path)
        thumbnail_url = await self._upload_thumbnail(data.thumblnail, thumbnail_path)

        async with self._session as session:
            game = await self._get_game_by_id(session, data.game_id)
            video = Videos(
                user_id=data.user_id,
                title=data.title,
                path=video_url,
                thumblnail_path=thumbnail_url,
                game=game,
            )
            session.add(video)
            await session.commit()
            await session.refresh(video)
            return video

    async def exists(self, path: str) -> bool:
        async with self._session as session:
            stmt = select(exists().where(Videos.path.like(f"%{path}")))
            result = await session.execute(stmt)
            return result.scalar()

    def _build_dir_path(self, user_id: int, title: str) -> str:
        return f"{user_id}/{self._dir_name}/{title}"

    def _build_video_path(self, dir_path: str, filename: str) -> str:
        return f"{dir_path}/{Path(filename).name}"

    async def _upload_thumbnail(self, thumblnail: bytes | None, path: str) -> str | None:
        if not thumblnail:
            return None
        return await self._s3_repository.upload_file(thumblnail, path)

    async def _get_game_by_id(self, session: AsyncSession, game_id: int) -> Games:
        query = await session.execute(select(Games).where(Games.id == game_id))
        return query.scalars().one()


class GamesRepository(AlchemyRepository):
    model = Games

    async def create_one(self, user: LingoplayUsers, game_data: GameCreate):
        game = Games(title=game_data.title)
        game.users.append(user)
        return await super().create_one(game)

    async def filter(
        self,
        user_id: int | None = None,
        title: str | None = None,
        id: int | None = None,
        first: bool = False,
    ) -> list[Games] | Games | None:
        async with self._session as session:
            query = select(self.model).options(selectinload(Games.users))

            if user_id is not None:
                query = query.join(Games.users).where(LingoplayUsers.id == user_id)

            if id is not None:
                query = query.where(Games.id == id)

            if title is not None:
                query = query.where(Games.title.ilike(f"%{title}%"))

            result = await session.execute(query)
            scalars = result.scalars()

            return scalars.first() if first else scalars.all()
