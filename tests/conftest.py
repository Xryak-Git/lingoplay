from collections.abc import AsyncGenerator

import pytest  # noqa: F401
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.core import Base, get_session
from src.main import app
from src.users.models import LingoplayUser
from src.users.schemas import UserCreate

TEST_DB_URI = "sqlite+aiosqlite:///:memory:"

TEST_USER_EMAIL = "test@example.com"
TEST_USERNAME = "Test User"
TEST_USER_PASSWORD = "123"


engine_test = create_async_engine(TEST_DB_URI, echo=False)
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def exsisting_user(prepare_test_db) -> AsyncGenerator[LingoplayUser, None]:
    """Создаёт тестового пользователя перед всеми тестами"""
    async for session in override_get_session():
        user_create = UserCreate(email=TEST_USER_EMAIL, username=TEST_USERNAME, password=TEST_USER_PASSWORD)
        user = LingoplayUser(email=user_create.email, username=user_create.username, password=user_create.password)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    yield user


@pytest_asyncio.fixture(scope="session")
async def prepare_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(prepare_test_db):
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
