from src.errors import AlreadyExistsError
from src.repository import AbstractRepository
from src.uploads.errors import VideoAlreadyUploadedError
from src.uploads.schemas import GameCreate, GameGet, VideoCreate
from src.users.models import LingoplayUsers


class UploadsService:
    def __init__(self, videos_repo: AbstractRepository, games_repo: AbstractRepository):
        self._videos_repo = videos_repo
        self._games_repo = games_repo

    async def add_video(self, video_create: VideoCreate):
        try:
            return await self._videos_repo.create_one(video_create)
        except AlreadyExistsError as e:
            raise VideoAlreadyUploadedError(video_create.title) from e

    async def add_game(self, user: LingoplayUsers, game_data: GameCreate) -> GameGet:
        result = await self._games_repo.create_one(user, game_data)
        return GameGet.model_validate(result, from_attributes=True)
