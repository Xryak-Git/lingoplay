from src import config
from src.repository import AbstractRepository


class VideoService:
    def __init__(self, repository: AbstractRepository):
        self._repository = repository
        self._url = config.S3_ENDPOINT_URL

    async def add(self, video):
        pass

    async def get(self, user_id: int):
        pass
