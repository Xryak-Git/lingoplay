from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import CurrentUser
from src.uploads.dependencies import UploadsServ
from src.uploads.errors import VideoAlreadyUploadedError
from src.uploads.schemas import GameCreate, GameGet, VideoCreate

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


@router.post("/games", status_code=201)
async def add_game(
    game_create: GameCreate,
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
) -> GameGet:
    """Adds new game users game"""

    return await uploads_serivce.add_game(current_user, game_create)


@router.get("/games")
async def games(
    current_user: CurrentUser,
    uploads_serivce: UploadsServ,
    all_games: bool = False,
    title: str | None = None,
) -> list[GameGet]:
    """Adds new game users game"""

    if all_games:
        return await uploads_serivce.get_all_games_with_search(title=title)
    return await uploads_serivce.get_games_with_search(user=current_user, title=title)
