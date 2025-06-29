from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import CurrentUser
from src.uploads.dependencies import video_service
from src.uploads.errors import VideoAlreadyUploadedError
from src.uploads.schemas import VideoCreate
from src.uploads.service import VideoService

router = APIRouter()


@router.post("/upload")
async def upload_video(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    game_id: Annotated[int, Form()],
    current_user: CurrentUser,
    video_service: Annotated[VideoService, Depends(video_service)],
) -> JSONResponse:
    """Creates new video and uploads to S3"""
    data = VideoCreate(file=file, title=title, game_id=game_id, user_id=current_user.id)

    try:
        await video_service.add(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content={"message": "Видео загружено и начало обрабатываться"}
        )
    except VideoAlreadyUploadedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=[{"msg": str(e)}]) from e


@router.post("/games")
async def add_game(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    game_id: Annotated[int, Form()],
    current_user: CurrentUser,
    video_service: Annotated[VideoService, Depends(video_service)],
) -> JSONResponse:
    """Creates new video and uploads to S3"""
    data = VideoCreate(file=file, title=title, game_id=game_id, user_id=current_user.id)

    try:
        await video_service.add(data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED, content={"message": "Видео загружено и начало обрабатываться"}
        )
    except VideoAlreadyUploadedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=[{"msg": str(e)}]) from e
