from typing import Annotated

from fastapi import APIRouter, File, Form, UploadFile

router = APIRouter()


@router.post("/upload")
async def upload_video(
    file: Annotated[UploadFile, File()],
    title: Annotated[str, Form()],
    type: Annotated[str, Form()],
):
    """Creates new video"""
    contents = await file.read()


    return {"filename": file.filename, "title": title, "type": type}
