import pytest  # noqa: F401
import pytest_asyncio
from fastapi import Response
from httpx import ASGITransport, AsyncClient

from src.database.core import get_session
from src.main import app
from src.repository import AbstractS3Repository, get_s3_repo
from tests.fixtures.db import override_get_session

pytest_plugins = [
    "tests.fixtures.db",
    "tests.fixtures.s3",
    "tests.fixtures.auth",
]


@pytest_asyncio.fixture(scope="function")
async def client(prepare_test_db, s3_test_repo: AbstractS3Repository):
    async def override_s3_repo():
        yield s3_test_repo

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_s3_repo] = override_s3_repo
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


class BaseTestClass:
    endpoint_prefix = ""

    @pytest_asyncio.fixture(scope="function")
    async def setup(self, client: AsyncClient, logined_user_headers: dict):
        self._client = client
        self._headers = logined_user_headers

    async def post(self, path: str, **kwargs) -> Response:
        return await self._client.post(f"{self.endpoint_prefix}{path}", headers=self._headers, **kwargs)

    async def get(self, path: str, **kwargs) -> Response:
        return await self._client.get(f"{self.endpoint_prefix}{path}", headers=self._headers, **kwargs)

    def assert_response_ok(self, response: Response, expected_code: int = 200):
        assert response.status_code == expected_code, response.text
