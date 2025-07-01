from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import CurrentUser
from src.uploads.dependencies import UploadsServ
from src.uploads.errors import VideoAlreadyUploadedError
from src.uploads.schemas import GameCreate, GameGet, GamesList, VideoCreate, VideoGet, VideosList

router = APIRouter()


@router.post("/videos")
async def upload_video(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    game_id: Annotated[int, Form()],
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
) -> JSONResponse:
    """Creates new video and uploads to S3"""
    data = VideoCreate(file=file, title=title, game_id=game_id, user_id=current_user.id)

    try:
        await uploads_serivce.add_video(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content={"message": "Видео загружено и начало обрабатываться"}
        )
    except VideoAlreadyUploadedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=[{"msg": str(e)}]) from e


@router.get("/videos")
async def get_users_videos(
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
) -> VideosList:
    """Gets users videos"""
    return await uploads_serivce.get_users_videos(user=current_user)


@router.get("/videos/{video_id}")
async def get_users_video(
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
    video_id: int,
) -> VideoGet:
    """Gets users videos"""
    return await uploads_serivce.get_users_video(user=current_user, id=video_id)


@router.post("/games", status_code=201)
async def add_game(
    game_create: GameCreate,
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
) -> GameGet:
    """Adds new game users game"""

    return await uploads_serivce.add_game(current_user, game_create)


@router.get("/games")
async def get_all_games(
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
    all: bool = False,
    title: str | None = None,
) -> GamesList:
    """Gets and filters users games or all games"""

    if all:
        return await uploads_serivce.get_all_games_with_search(title=title)
    return await uploads_serivce.get_games_with_search(user=current_user, title=title)


@router.get("/games/{game_id}")
async def get_users_game(
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
    game_id: int,
) -> GameGet:
    """Adds new game users game"""
    return await uploads_serivce.get_games_with_search(user=current_user, id=game_id)
