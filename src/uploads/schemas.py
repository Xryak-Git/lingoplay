from fastapi import UploadFile
from pydantic import BaseModel


class VideoCreate(BaseModel):
    user_id: int
    file: UploadFile
    title: str
    game_id: int


class VideoWriteDb(BaseModel):
    user_id: int
    path: str
    title: str

class VideoGet(VideoWriteDb):
    id: int
    game_id: int

class VideosList(BaseModel):
    list: list[VideoGet]


class GameCreate(BaseModel):
    title: str


class GameGet(GameCreate):
    id: int


class GamesList(BaseModel):
    list: list[GameGet]
