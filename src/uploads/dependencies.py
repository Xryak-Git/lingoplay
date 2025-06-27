from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src import config
from src.database.core import get_session
from src.repository import S3Repository
from src.uploads.repository import VideoRepository
from src.uploads.service import VideoService


async def video_service(session: Annotated[AsyncSession, Depends(get_session)]):
    return VideoService(
        repository=VideoRepository(
            session,
            s3_repository=S3Repository(
                access_key=config.S3_ACCESS_KEY,
                secret_key=config.S3_SECRET_KEY,
                endpoint_url=config.S3_ENDPOINT_URL,
                bucket_name=config.S3_BUCKET_NAME,
            ),
        )
    )
