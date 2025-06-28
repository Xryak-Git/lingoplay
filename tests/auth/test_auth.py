import pytest
from httpx import AsyncClient

from src.users.schemas import UserLogin
from tests.conftest import TEST_USER_EMAIL, TEST_USER_PASSWORD


class TestAuthRoutes:
    _test_user_email = "test@mail.ru"
    _test_password = "secret123"
    _test_username = "test_user"

    @pytest.mark.asyncio
    async def test_register_and_login(self, client: AsyncClient):
        # Регистрация
        user_data = {"email": self._test_user_email, "username": self._test_username, "password": self._test_password}

        register_response = await client.post("/auth/registrate", json=user_data)

        assert register_response.status_code == 201, register_response.text

        # Логин
        ul = UserLogin(email=self._test_user_email, password=self._test_password)
        login_response = await client.post("/auth/login", json=ul.model_dump())

        assert login_response.status_code == 200, login_response.text
        login_data = login_response.json()

        assert "token" in login_data
        assert "user" in login_data
        assert login_data["user"]["email"] == self._test_user_email

        token = login_response.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Получение текущего пользователя
        current_response = await client.get("/users/current", headers=headers)
        assert current_response.status_code == 200, current_response.text

        current_user = current_response.json()
        assert current_user["email"] == self._test_user_email
        assert current_user["username"] == self._test_username

    @pytest.mark.asyncio
    async def test_create_existing_user(self, client: AsyncClient):
        user_data = {"email": self._test_user_email, "username": self._test_username, "password": self._test_password}

        register_response = await client.post("/auth/registrate", json=user_data)

        assert register_response.status_code == 409, register_response.text


    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "email, password, code",
        [
            (TEST_USER_EMAIL, TEST_USER_PASSWORD, 200),
            ("wrong@mail.ru", TEST_USER_PASSWORD, 401),
            (TEST_USER_EMAIL, "wrongpass", 401),
            ("", "", 422),
            ("test@mail.ru", "", 422),
        ],
    )
    async def test_user_login_cases(self, client: AsyncClient, email: str, password: str, code: int):
        payload = {"email": email, "password": password}
        response = await client.post("/auth/login", json=payload)
        assert response.status_code == code, response.text
