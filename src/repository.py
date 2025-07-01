import re
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import wraps
from typing import Annotated, overload

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from fastapi import Depends
from sqlalchemy import delete, exists, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from types_aiobotocore_s3.client import S3Client

from src import config
from src.database.core import Base
from src.errors import DatabaseCommitError, UniqueConstraintViolation


class AbstractRepository(ABC):
    @abstractmethod
    async def get_by():
        raise NotImplementedError

    @abstractmethod
    async def get_by_or():
        raise NotImplementedError

    @abstractmethod
    async def get_all():
        raise NotImplementedError

    @abstractmethod
    async def create_one():
        raise NotImplementedError

    @abstractmethod
    async def update_or_create():
        raise NotImplementedError

    @abstractmethod
    async def update_by():
        raise NotImplementedError

    @abstractmethod
    async def exists():
        raise NotImplementedError

    @abstractmethod
    async def filter():
        raise NotImplementedError


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


async def get_s3_repo():
    yield S3Repository(
        access_key=config.S3_ACCESS_KEY,
        secret_key=config.S3_SECRET_KEY,
        endpoint_url=config.S3_ENDPOINT_URL,
        bucket_name=config.S3_BUCKET_NAME,
    )


S3Repo = Annotated[AbstractS3Repository, Depends(get_s3_repo)]


def handle_integrity_errors(method):
    @wraps(method)
    async def wrapper(self, *args, **kwargs):
        async with self._session as session:
            try:
                return await method(self, session, *args, **kwargs)
            except IntegrityError as e:
                await session.rollback()
                error_message = str(e.orig)

                field_name = self._extract_unique_field_from_message(error_message)
                if field_name:
                    source = args[0] if args else kwargs
                    if isinstance(source, dict):
                        value = source.get(field_name, "???")
                    else:
                        value = getattr(source, field_name, "???")

                    raise UniqueConstraintViolation(field_name, value) from e

                raise DatabaseCommitError() from e

    return wrapper


class AlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[Base]:
        async with self._session as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            return res.scalars().all()

    async def filter(self, **kwargs) -> list[Base]:
        async with self._session as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)
            return result.all()

    @overload
    async def create_one(self, session: AsyncSession, data: dict) -> Base: ...

    @overload
    async def create_one(self, session: AsyncSession, instance: Base) -> Base: ...

    @handle_integrity_errors
    async def create_one(self, session: AsyncSession, data_or_instance: dict | Base):
        if isinstance(data_or_instance, dict):
            stmt = insert(self.model).values(**data_or_instance).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()
        else:
            session.add(data_or_instance)
            await session.commit()
            await session.refresh(data_or_instance)
            return data_or_instance

    async def get_by(self, **kwargs):
        async with self._session as session:
            query = select(self.model).filter_by(**kwargs)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def update_by(self, **kwargs) -> int:
        async with self._session as session:
            stmt = update(self.model).filter_by(**kwargs)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def update_or_create(self, filters: dict, values: dict):
        async with self._session as session:
            instance = await self.get_by(**filters)

            if instance:
                stmt = update(self.model).filter_by(**filters).values(**values).returning(self.model)
                result = await session.execute(stmt)
                await session.commit()
                updated_instance = result.scalar_one()
                return updated_instance, False

            try:
                create_data = {**filters, **values}
                stmt = insert(self.model).values(**create_data).returning(self.model)
                result = await session.execute(stmt)
                await session.commit()
                new_instance = result.scalar_one()
                return new_instance, True
            except IntegrityError:
                await session.rollback()
                result = await session.execute(select(self.model).filter_by(**filters))
                instance = result.scalar_one()
                return instance, False

    async def delete_by(self, **kwargs) -> int:
        async with self._session as session:
            stmt = delete(self.model).filter_by(**kwargs)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def get_by_or(self, **kwargs):
        async with self._session as session:
            conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
            stmt = select(self.model).where(or_(*conditions))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def exists(self, **kwargs) -> bool:
        async with self._session as session:
            stmt = select(exists().filer_by(**kwargs))
            result = await session.execute(stmt)
            return result.scalar()

    def _extract_unique_field_from_message(self, message: str) -> str | None:
        match = re.search(r"UNIQUE constraint failed: [\w_]+\.(\w+)", message)
        if match:
            return match.group(1)

        match = re.search(r"Key \((\w+)\)=\(.+\) already exists", message)
        if match:
            return match.group(1)

        match = re.search(r"for key '(\w+)'", message)
        if match:
            return match.group(1)

        return None


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

    @property
    def url(self):
        return self.config.get("endpoint_url")
