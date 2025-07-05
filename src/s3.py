from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from tempfile import NamedTemporaryFile
from typing import Annotated

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import Depends
from types_aiobotocore_s3.client import S3Client

from src import config


class AbstractS3Repository(ABC):
    @abstractmethod
    async def get_file():
        raise NotImplementedError

    @abstractmethod
    async def upload_file():
        raise NotImplementedError

    @abstractmethod
    async def delete_file():
        raise NotImplementedError

    @abstractmethod
    async def download_to_tempfile():
        raise NotImplementedError


async def get_s3_repo():
    yield S3Repository(
        access_key=config.S3_ACCESS_KEY,
        secret_key=config.S3_SECRET_KEY,
        endpoint_url=config.S3_ENDPOINT_URL,
        bucket_name=config.S3_BUCKET_NAME,
    )


S3Repo = Annotated[AbstractS3Repository, Depends(get_s3_repo)]


class S3Repository(AbstractS3Repository):
    def __init__(self, access_key: str, secret_key: str, endpoint_url: str, bucket_name: str):
        self.config = {
            "aws_access_key_id": access_key,
            "aws_secret_access_key": secret_key,
            "endpoint_url": endpoint_url,
        }
        self.bucket_name = bucket_name
        self.session = get_session()

    @asynccontextmanager
    async def _get_client(self) -> AsyncGenerator[S3Client, None]:
        async with self.session.create_client("s3", **self.config) as client:
            yield client

    async def get_file(self, key: str):
        async with self._get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=key)
            return await response["Body"].read()

    async def get_all(self):
        async with self._get_client() as client:
            response = await client.list_objects_v2(Bucket=self.bucket_name)
            return [item["Key"] for item in response.get("Contents", [])]

    async def upload_file(self, file_obj, object_name: str) -> str:
        try:
            async with self._get_client() as client:
                await client.put_object(Bucket=self.bucket_name, Key=object_name, Body=file_obj)
            return f"{self.config['endpoint_url'].rstrip('/')}/{self.bucket_name}/{object_name}"
        except ClientError as e:
            print(f"Error uploading file: {e}")

    async def delete_file(self, object_name: str):
        try:
            async with self._get_client() as client:
                await client.delete_object(Bucket=self.bucket_name, Key=object_name)
        except ClientError as e:
            print(f"Error deleting file: {e}")

    async def download_to_tempfile(self, key) -> str:
        async with self._get_client() as client:
            response = await client.get_object(Bucket=self.bucket_name, Key=key)
            temp = NamedTemporaryFile(delete=False, suffix=".mp4")
            async for chunk in response["Body"].iter_chunks():
                temp.write(chunk)
            temp.close()
            return temp.name

    @property
    def url(self):
        return self.config.get("endpoint_url")
