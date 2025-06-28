from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.repository import S3Repo
from src.uploads.repository import VideoRepository
from src.uploads.service import VideoService


async def video_service(session: Annotated[AsyncSession, Depends(get_session)], s3_repository: S3Repo):
    return VideoService(repository=VideoRepository(session, s3_repository=s3_repository))
