from collections.abc import AsyncGenerator
from pathlib import Path

import pytest  # noqa: F401
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import ROOT_DIR
from src.database.core import Base, get_session
from src.main import app
from src.repository import AbstractS3Repository, get_s3_repo
from src.uploads.models import Games
from src.users.models import LingoplayUser
from src.users.schemas import UserCreate

TEST_DB_URI = "sqlite+aiosqlite:///:memory:"

TEST_USER_EMAIL = "test@example.com"
TEST_USERNAME = "Test User"
TEST_USER_PASSWORD = "123"

TEST_DATA_DIR = ROOT_DIR / "tests" / "testdata"


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


@pytest_asyncio.fixture(scope="session", autouse=True)
async def existing_games(prepare_test_db) -> AsyncGenerator[Games, None]:
    """Создаёт тестовыую игру всеми тестами"""
    async for session in override_get_session():
        game = Games(title="kek")
        session.add(game)
        await session.commit()
        await session.refresh(game)

    yield game


@pytest_asyncio.fixture(scope="session")
async def prepare_test_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def s3_test_repo() -> AsyncGenerator[AbstractS3Repository, None]:
    repo = LocalFolderRepository(folder_path=TEST_DATA_DIR)
    yield repo


@pytest_asyncio.fixture(scope="function")
async def client(prepare_test_db, s3_test_repo: AbstractS3Repository):
    async def override_s3_repo():
        yield s3_test_repo

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_s3_repo] = override_s3_repo
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()


class LocalFolderRepository(AbstractS3Repository):
    def __init__(self, folder_path: Path):
        self.folder_path = folder_path
        self.folder_path.mkdir(parents=True, exist_ok=True)

        self._last_file_path: Path = None

    async def get_file(self) -> bytes:
        file_path = self._last_file_path
        if not file_path.exists():
            raise FileNotFoundError(f"No such file: {file_path}")
        return file_path.read_bytes()

    async def get_all(self) -> list[str]:
        return [f.name for f in self.folder_path.iterdir() if f.is_file()]

    async def upload_file(self, file_obj, object_name: str) -> str:
        file_path = self.folder_path / object_name
        dir_path = file_path.parent
        dir_path.mkdir(parents=True, exist_ok=True)

        print("Saving to:", file_path)
        self._last_file_path = file_path
        data = file_obj.read()

        file_path.write_bytes(data)
        return str(file_path.resolve())

    async def delete_file(self, object_name: str):
        file_path = self.folder_path / object_name
        if file_path.exists():
            file_path.unlink()

    @property
    def url(self) -> str:
        return str(self.folder_path.resolve())
