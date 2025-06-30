from collections.abc import AsyncGenerator

import pytest  # noqa: F401
import pytest_asyncio
from httpx import AsyncClient

from src.users.schemas import UserLogin
from tests.constants import TEST_USER_EMAIL, TEST_USER_PASSWORD


@pytest_asyncio.fixture(scope="function")
async def logined_user_headers(client: AsyncClient) -> AsyncGenerator[dict, None]:
    """Заголовки с токеном тестового пользователя"""
    ul = UserLogin(email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD)
    login_response = await client.post("/auth/login", json=ul.model_dump())
    assert login_response.status_code == 200, login_response.text

    token = login_response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    yield headers
