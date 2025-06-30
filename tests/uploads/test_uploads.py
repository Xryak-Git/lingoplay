import io

import pytest
from httpx import AsyncClient

from src.repository import AbstractS3Repository
from src.uploads.models import Games
from src.uploads.schemas import GameCreate


class TestUploadsRoutes:

    @pytest.mark.asyncio
    async def test_video_upload(
        self, client: AsyncClient, existing_game: Games, s3_test_repo: AbstractS3Repository, logined_user_headers: dict
    ):

        fake_video = io.BytesIO(b"fake mp4 data")
        fake_video.name = "test_video.mp4"

        response = await client.post(
            "/videos/upload",
            headers=logined_user_headers,
            files={"file": ("test_video.mp4", fake_video, "video/mp4")},
            data={"title": "TestVideo", "game_id": f"{existing_game.id}"},
        )

        assert response.status_code == 201, response.text
        assert response.json()["message"] == "Видео загружено и начало обрабатываться"
        assert await s3_test_repo.get_file() == fake_video.getvalue()

    @pytest.mark.asyncio
    async def test_add_game(self, client: AsyncClient, logined_user_headers: dict):
        test_game = GameCreate(title="Persona 5 Royal")

        response = await client.post(
            "/videos/games",
            headers=logined_user_headers,
            json=test_game.model_dump(),
        )

        assert response.status_code == 201, response.text
