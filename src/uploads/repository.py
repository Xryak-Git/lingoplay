from pathlib import Path

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.errors import AlreadyExistsError
from src.repository import AbstractS3Repository, AlchemyRepository
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
        path = f"{data.user_id}/{self._dir_name}/{data.title}{Path(data.file.filename).suffix}"

        if await self.exists(path=path):
            raise AlreadyExistsError(self.model.__tablename__, "path", path)

        url = await self._s3_repository.upload_file(data.file.file, path)

        async with self._session as session:
            result = await session.execute(select(Games).where(Games.id == data.game_id))
            game = result.scalars().one()

            video = Videos(user_id=data.user_id, path=url, title=data.title, game=game)
            session.add(video)
            await session.commit()
            await session.refresh(video)
            return video

    async def exists(self, path: str):
        async with self._session as session:
            stmt = select(exists().where(Videos.path.like(f"%{path}")))
            result = await session.execute(stmt)
            return result.scalar()


class GamesRepository(AlchemyRepository):
    model = Games

    async def create_one(self, user: LingoplayUsers, game_data: GameCreate):
        game = Games(title=game_data.title)
        game.users.append(user)
        return await super().create_one(game)

    async def filter(self, user_id: int | None = None, title: str | None = None, id: int | None = None) -> list[Games]:
        async with self._session as session:
            query = select(self.model).options(selectinload(Games.users))

            if user_id:
                query = query.join(Games.users).where(LingoplayUsers.id == user_id)

            if title:
                query = query.where(Games.title.ilike(f"%{title}%"))

            if id:
                query = query.where(Games.id == id)

            res = await session.execute(query)

            return res.scalars().all()
