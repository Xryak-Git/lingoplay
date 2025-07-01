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
    uploads_service: UploadsServ,
) -> JSONResponse:
    """Upload new video and send it for processing"""
    data = VideoCreate(file=file, title=title, game_id=game_id, user_id=current_user.id)

    try:
        await uploads_service.add_video(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content={"message": "Видео загружено и начало обрабатываться"}
        )
    except VideoAlreadyUploadedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[{"msg": str(e)}],
        ) from e


@router.get("/videos", response_model=VideosList)
async def get_user_videos(
    current_user: CurrentUser,
    uploads_service: UploadsServ,
) -> VideosList:
    """Get all videos uploaded by current user"""
    return await uploads_service.get_user_videos(user=current_user)


@router.get("/videos/{video_id}", response_model=VideoGet)
async def get_user_video(
    video_id: int,
    current_user: CurrentUser,
    uploads_service: UploadsServ,
) -> VideoGet:
    """Get specific video of current user by ID"""
    return await uploads_service.get_user_video(user=current_user, video_id=video_id)


@router.post("/games", response_model=GameGet, status_code=status.HTTP_201_CREATED)
async def add_game(
    game_create: GameCreate,
    current_user: CurrentUser,
    uploads_service: UploadsServ,
) -> GameGet:
    """Add new game for current user"""
    return await uploads_service.add_game(current_user, game_create)


@router.get("/games", response_model=GamesList)
async def get_games(
    current_user: CurrentUser,
    uploads_service: UploadsServ,
    all: bool = False,
    title: str | None = None,
) -> GamesList:
    """Get games — either user-specific or all, with optional filtering"""
    if all:
        return await uploads_service.search_all_games(title=title)
    return await uploads_service.search_user_games(user=current_user, title=title)


@router.get("/games/{game_id}", response_model=GameGet)
async def get_user_game(
    game_id: int,
    current_user: CurrentUser,
    uploads_service: UploadsServ,
) -> GameGet:
    """Get specific game of current user by ID"""
    return await uploads_service.get_user_game(user=current_user, game_id=game_id)
