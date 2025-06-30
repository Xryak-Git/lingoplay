from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.repository import S3Repo
from src.uploads.repository import GamesRepository, VideoRepository
from src.uploads.service import UploadsService


async def uploads_service(session: Annotated[AsyncSession, Depends(get_session)], s3_repository: S3Repo):
    return UploadsService(videos_repo=VideoRepository(session, s3_repository), games_repo=GamesRepository(session))
