from collections.abc import AsyncGenerator

import pytest  # noqa: F401
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.database.core import Base
from src.uploads.models import Games, Videos
from src.users.models import LingoplayUsers
from src.users.schemas import UserCreate
from tests.constants import TEST_DB_URI, TEST_USER_EMAIL, TEST_USER_PASSWORD, TEST_USERNAME

engine_test = create_async_engine(TEST_DB_URI, echo=False)
async_session_maker = async_sessionmaker(engine_test, expire_on_commit=False)


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


@pytest_asyncio.fixture(scope="session", autouse=True)
async def exsisting_user(prepare_test_db) -> AsyncGenerator[LingoplayUsers, None]:
    """Создаёт тестового пользователя перед всеми тестами"""
    async for session in override_get_session():
        user_create = UserCreate(email=TEST_USER_EMAIL, username=TEST_USERNAME, password=TEST_USER_PASSWORD)
        user = LingoplayUsers(email=user_create.email, username=user_create.username, password=user_create.password)
        session.add(user)
        await session.commit()
        await session.refresh(user)

    yield user


@pytest_asyncio.fixture(scope="session", autouse=True)
async def existing_game(prepare_test_db, exsisting_user: LingoplayUsers) -> AsyncGenerator[Games, None]:
    """Создаёт тестовыую игру всеми тестами"""
    async for session in override_get_session():
        game = Games(title="kek")
        game.users.append(exsisting_user)
        session.add(game)
        await session.commit()
        await session.refresh(game)

    yield game


@pytest_asyncio.fixture(scope="session", autouse=True)
async def existing_video(
    prepare_test_db, exsisting_user: LingoplayUsers, existing_game: Games
) -> AsyncGenerator[Videos, None]:
    """Создаёт тестовыую игру всеми тестами"""
    async for session in override_get_session():
        video = Videos(title="pek", path="video.mp4", user_id=exsisting_user.id, game_id=existing_game.id)
        session.add(video)
        await session.commit()
        await session.refresh(video)

    yield video


@pytest_asyncio.fixture(scope="session")
async def prepare_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
