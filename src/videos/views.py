from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile

from src.videos.repository import S3Client, video_repository

router = APIRouter()


@router.post("/upload")
async def upload_video(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    type: Annotated[str, Form()],
    s3_client: Annotated[S3Client, Depends(video_repository)],
):
    """Creates new video and uploads to S3"""
    object_name = file.filename
    await s3_client.upload_file(file_obj=file.file, object_name=object_name)

    return {"filename": file.filename, "title": title, "type": type}
