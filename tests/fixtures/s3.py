from collections.abc import AsyncGenerator
from pathlib import Path

import pytest  # noqa: F401
import pytest_asyncio

from src.repository import AbstractS3Repository
from tests.constants import TEST_DATA_DIR


@pytest_asyncio.fixture(scope="function")
async def s3_test_repo() -> AsyncGenerator[AbstractS3Repository, None]:
    repo = LocalFolderRepository(folder_path=TEST_DATA_DIR)
    yield repo


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
