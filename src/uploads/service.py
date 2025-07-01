from src.errors import AlreadyExistsError
from src.repository import AbstractRepository
from src.uploads.errors import VideoAlreadyUploadedError
from src.uploads.schemas import GameCreate, GameGet, GamesList, VideoCreate, VideoGet, VideosList
from src.users.models import LingoplayUsers


class UploadsService:
    def __init__(self, videos_repo: AbstractRepository, games_repo: AbstractRepository):
        self._videos_repo = videos_repo
        self._games_repo = games_repo

    # Videos
    async def add_video(self, video_create: VideoCreate):
        try:
            return await self._videos_repo.create_one(video_create)
        except AlreadyExistsError as e:
            raise VideoAlreadyUploadedError(video_create.title) from e

    async def get_users_video(self, user: LingoplayUsers, id: int) -> VideoGet:
        result = await self._videos_repo.filter(user_id=user.id, id=id, first=True)
        return VideoGet.model_validate(result, from_attributes=True)

    async def get_users_videos(self, user: LingoplayUsers) -> VideosList:
        result = await self._videos_repo.filter(user_id=user.id)
        video_get_list = [VideoGet.model_validate(row, from_attributes=True) for row in result]
        return VideosList.model_validate({"list": video_get_list})

    # Games
    async def add_game(self, user: LingoplayUsers, game_data: GameCreate) -> GameGet:
        result = await self._games_repo.create_one(user, game_data)
        return GameGet.model_validate(result, from_attributes=True)

    async def get_users_game(self, user: LingoplayUsers, id: int) -> GameGet:
        result = await self._games_repo.filter(user_id=user.id, id=id)
        return GameGet.model_validate(result, from_attributes=True)

    async def get_games_with_search(self, user: LingoplayUsers, **kwargs) -> GamesList:
        result = await self._games_repo.filter(user_id=user.id, **kwargs)
        game_get_list = [GameGet.model_validate(row, from_attributes=True) for row in result]
        return GamesList.model_validate({"list": game_get_list})

    async def get_all_games_with_search(self, **kwargs) -> GamesList:
        result = await self._games_repo.filter(**kwargs)
        game_get_list = [GameGet.model_validate(row, from_attributes=True) for row in result]
        return GamesList.model_validate({"list": game_get_list})
