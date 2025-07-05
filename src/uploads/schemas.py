from fastapi import UploadFile
from pydantic import BaseModel


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
