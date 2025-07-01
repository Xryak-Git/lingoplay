import io

import pytest
from fastapi import Response

from src.repository import AbstractS3Repository
from src.uploads.models import Games, Videos
from src.uploads.schemas import GameCreate
from tests.conftest import BaseTestClass


class TestUploadsRoutes(BaseTestClass):
    endpoint_prefix = "/uploads"

    def get_json_list(self, response: Response) -> list:
        return response.json().get("list", [])

    @pytest.mark.asyncio
    async def test_video_upload(self, setup, existing_game: Games, s3_test_repo: AbstractS3Repository):
        fake_video = io.BytesIO(b"fake mp4 data")
        fake_video.name = "test_video.mp4"

        response = await self.post(
            "/videos",
            files={"file": ("test_video.mp4", fake_video, "video/mp4")},
            data={"title": "TestVideo", "game_id": str(existing_game.id)},
        )

        self.assert_response_ok(response, 201)
        assert response.json()["message"] == "Видео загружено и начало обрабатываться"
        assert await s3_test_repo.get_file() == fake_video.getvalue()

    @pytest.mark.asyncio
    async def test_add_game(self, setup):
        response = await self.post(
            "/games",
            json=GameCreate(title="Persona 5 Royal").model_dump(),
        )
        self.assert_response_ok(response, 201)

        response = await self.get("/games")
        self.assert_response_ok(response)
        assert "Persona 5 Royal" in response.text

    @pytest.mark.asyncio
    async def test_get_users_videos(self, setup, existing_video: Videos):
        response = await self.get("/videos")
        self.assert_response_ok(response)
        assert existing_video.title in self.get_json_list(response)[0].get("title", "")

    @pytest.mark.asyncio
    async def test_get_users_video(self, setup, existing_video: Videos):
        response = await self.get(f"/videos/{existing_video.id}")
        self.assert_response_ok(response)
        assert response.json()["id"] == existing_video.id

    @pytest.mark.asyncio
    async def test_get_all_games(self, setup, existing_game: Games):
        response = await self.get("/games?all=true")
        self.assert_response_ok(response)
        assert any(existing_game.title in g["title"] for g in self.get_json_list(response))

    @pytest.mark.asyncio
    async def test_get_filtered_games_by_title(self, setup, existing_game: Games):
        response = await self.get(f"/games?title={existing_game.title}")
        self.assert_response_ok(response)
        assert all(existing_game.title in g["title"] for g in self.get_json_list(response))

    @pytest.mark.asyncio
    async def test_get_users_game_by_id(self, setup, existing_game: Games):
        response = await self.get(f"/games/{existing_game.id}")
        self.assert_response_ok(response)
        assert response.json()["id"] == existing_game.id
