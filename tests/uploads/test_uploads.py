import io

import pytest
from httpx import AsyncClient

from src.repository import AbstractS3Repository
from src.uploads.models import Games, Videos
from src.uploads.schemas import GameCreate


class TestUploadsRoutes:
    @pytest.mark.asyncio
    async def test_video_upload(
        self, client: AsyncClient, existing_game: Games, s3_test_repo: AbstractS3Repository, logined_user_headers: dict
    ):
        fake_video = io.BytesIO(b"fake mp4 data")
        fake_video.name = "test_video.mp4"

        response = await client.post(
            "/uploads/videos",
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
            "/uploads/games",
            headers=logined_user_headers,
            json=test_game.model_dump(),
        )

        assert response.status_code == 201, response.text

        response = await client.get(
            "/uploads/games",
            headers=logined_user_headers,
        )

        assert response.status_code == 200, "Persona 5 Royal" in response.text

    @pytest.mark.asyncio
    async def test_get_users_videos(self, client: AsyncClient, logined_user_headers: dict, existing_video: Videos):
        response = await client.get("/uploads/videos", headers=logined_user_headers)

        assert response.status_code == 200
        assert existing_video.title in response.json()["list"][0].get("title", "")

    @pytest.mark.asyncio
    async def test_get_users_video(self, client: AsyncClient, logined_user_headers: dict, existing_video: Videos):
        response = await client.get(f"/uploads/videos/{existing_video.id}", headers=logined_user_headers)

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["id"] == existing_video.id

    @pytest.mark.asyncio
    async def test_get_all_games(self, client: AsyncClient, logined_user_headers: dict, existing_game: Games):
        response = await client.get("/uploads/games?all=true", headers=logined_user_headers)
        response_list = response.json()["list"]
        assert response.status_code == 200
        assert isinstance(response_list, list)
        assert any(existing_game.title in item["title"] for item in response_list)

    @pytest.mark.asyncio
    async def test_get_filtered_games_by_title(self, client: AsyncClient, logined_user_headers: dict, existing_game: Games):
        response = await client.get(f"/uploads/games?title={existing_game.title}", headers=logined_user_headers)

        assert response.status_code == 200
        games = response.json()["list"]
        assert all(existing_game.title in game["title"] for game in games)

    @pytest.mark.asyncio
    async def test_get_users_game_by_id(self, client: AsyncClient, logined_user_headers: dict, existing_game: Games):
        response = await client.get(f"/uploads/games/{existing_game.id}", headers=logined_user_headers)

        assert response.status_code == 200
        assert response.json()["id"] == existing_game.id
