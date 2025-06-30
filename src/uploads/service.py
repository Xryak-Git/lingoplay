from src.errors import AlreadyExistsError
from src.repository import AbstractRepository
from src.uploads.errors import VideoAlreadyUploadedError
from src.uploads.schemas import VideoCreate


class UploadsService:
    def __init__(self, videos_repo: AbstractRepository, games_repo: AbstractRepository):
        self._videos_repo = videos_repo
        self._games_repo = games_repo

    async def add_video(self, video_create: VideoCreate):
        try:
            return await self._videos_repo.create_one(video_create)
        except AlreadyExistsError as e:
            raise VideoAlreadyUploadedError(video_create.title) from e
