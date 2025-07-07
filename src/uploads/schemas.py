from fastapi import UploadFile
from pydantic import BaseModel

from src.uploads.models import Videos


class VideoCreate(BaseModel):
    user_id: int
    video: UploadFile
    title: str
    game_id: int
    thumblnail: bytes | None = None


class VideoGet(BaseModel):
    id: int
    game_id: int
    user_id: int
    path: str
    thumblnail_path: str | None = None
    title: str


class VideosList(BaseModel):
    list: list[VideoGet]


class GameCreate(BaseModel):
    title: str


class GameGet(GameCreate):
    id: int


class GamesList(BaseModel):
    list: list[GameGet]


class LingoplayImage(BaseModel):
    video: Videos
    path: str
    text: str

    class Config:
        arbitrary_types_allowed = True
