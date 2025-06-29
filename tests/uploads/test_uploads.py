import io

import pytest
from httpx import AsyncClient

from src.repository import AbstractS3Repository
from src.uploads.models import Games
from src.users.schemas import UserLogin
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


class TestUploadsRoutes:
    _test_user_email = "test@example.com"

    @pytest.mark.asyncio
    async def test_video_upload(self, client: AsyncClient, existing_games: Games, s3_test_repo: AbstractS3Repository):
        # Логины
        ul = UserLogin(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
        login_response = await client.post("/auth/login", json=ul.model_dump())
        assert login_response.status_code == 200, login_response.text

        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Подготовка файла и данных формы
        fake_video = io.BytesIO(b"fake mp4 data")
        fake_video.name = "test_video.mp4"

        response = await client.post(
            "/videos/upload",
            headers=headers,
            files={"file": ("test_video.mp4", fake_video, "video/mp4")},
            data={
                "title": "TestVideo",
                "game_ids": f"{existing_games.id}"
            },
        )


        assert response.status_code == 201, response.text
        assert response.json()["message"] == "Видео загружено и начало обрабатываться"
        assert await s3_test_repo.get_file() == fake_video.getvalue()
