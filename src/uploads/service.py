from src.errors import AlreadyExistsError
from src.repository import AbstractRepository
from src.uploads.errors import VideoAlreadyUploadedError
from src.uploads.schemas import VideoCreate


class VideoService:
    def __init__(self, repository: AbstractRepository):
        self._repository = repository

    async def add(
        self,
        data: VideoCreate,
    ):
        try:
            return await self._repository.create_one(data)
        except AlreadyExistsError as e:
            raise VideoAlreadyUploadedError(data.title) from e
