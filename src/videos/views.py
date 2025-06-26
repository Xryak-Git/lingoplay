from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.auth.dependencies import CurrentUser
from src.videos.dependencies import video_service
from src.videos.service import VideoService

router = APIRouter()


@router.post("/upload")
async def upload_video(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    type: Annotated[str, Form()],
    current_user: CurrentUser,
    video_service: Annotated[VideoService, Depends(video_service)],
):
    """Creates new video and uploads to S3"""
    object_name = file.filename
    await video_service.add(file_obj=file.file, object_name=object_name, user=current_user)

    return {"filename": file.filename, "title": title, "type": type}


# @router.get("/")
# async def all_videos(
#     s3_client: Annotated[S3Repository, Depends(video_repository)],
# ):
#     """Creates new video and uploads to S3"""
#     data = await s3_client.get_by(key="Pictures/1.gif")
#     print(data)

#     return data
