from fastapi import UploadFile
from pydantic import BaseModel


class VideoCreate(BaseModel):
    user_id: int
    file: UploadFile
    title: str
    game_ids: set[int]

class VideoWriteDb(BaseModel):
    user_id: int
    path: str
    title: str
