from src.repository import AbstractRepository
from src.videos.schemas import VideoCreate


class VideoService:
    def __init__(self, repository: AbstractRepository):
        self._repository = repository

    async def add(
        self,
        data: VideoCreate,
    ):
        return await self._repository.create_one(data)
