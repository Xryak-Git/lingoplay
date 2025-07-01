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
    async def add_video(self, video_create: VideoCreate) -> VideoGet:
        try:
            video = await self._videos_repo.create_one(video_create)
            return VideoGet.model_validate(video, from_attributes=True)
        except AlreadyExistsError as e:
            raise VideoAlreadyUploadedError(video_create.title) from e

    async def get_user_video(self, user: LingoplayUsers, video_id: int) -> VideoGet:
        video = await self._videos_repo.filter(user_id=user.id, id=video_id, first=True)
        return VideoGet.model_validate(video, from_attributes=True)

    async def get_user_videos(self, user: LingoplayUsers) -> VideosList:
        videos = await self._videos_repo.filter(user_id=user.id)
        return VideosList.model_validate({"list": [VideoGet.model_validate(v, from_attributes=True) for v in videos]})

    # Games
    async def add_game(self, user: LingoplayUsers, game_data: GameCreate) -> GameGet:
        game = await self._games_repo.create_one(user, game_data)
        return GameGet.model_validate(game, from_attributes=True)

    async def get_user_game(self, user: LingoplayUsers, game_id: int) -> GameGet:
        game = await self._games_repo.filter(user_id=user.id, id=game_id, first=True)
        return GameGet.model_validate(game, from_attributes=True)

    async def search_user_games(self, user: LingoplayUsers, **kwargs) -> GamesList:
        games = await self._games_repo.filter(user_id=user.id, **kwargs)
        return GamesList.model_validate({"list": [GameGet.model_validate(g, from_attributes=True) for g in games]})

    async def search_all_games(self, **kwargs) -> GamesList:
        games = await self._games_repo.filter(**kwargs)
        return GamesList.model_validate({"list": [GameGet.model_validate(g, from_attributes=True) for g in games]})
