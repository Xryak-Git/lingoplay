import re
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aiobotocore.session import get_session
from botocore.exceptions import ClientError
from sqlalchemy import and_, delete, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from types_aiobotocore_s3.client import S3Client

from src.database.core import new_session
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


class AlchemyRepository(AbstractRepository):
    model = None

    async def get_all(self):
        async with new_session() as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            res = [row[0].dict() for row in res.all()]
            return res

    async def create_one(self, data: dict):
        async with new_session() as session:
            try:
                stmt = insert(self.model).values(**data).returning(self.model)
                res = await session.execute(stmt)
                await session.commit()
                return res.scalar_one()
            except IntegrityError as e:
                await session.rollback()
                error_message = str(e.orig)

                field_name = self._extract_unique_field_from_message(error_message)
                if field_name:
                    raise UniqueConstraintViolation(field_name, data.get(field_name, "???")) from e

                raise DatabaseCommitError() from e

    async def get_by(self, **kwargs):
        async with new_session() as session:
            conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
            stmt = select(self.model).where(and_(*conditions))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    async def update_by(self, filters: dict, values: dict) -> int:
        async with new_session() as session:
            conditions = [getattr(self.model, key) == value for key, value in filters.items()]
            stmt = update(self.model).where(and_(*conditions)).values(**values)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def update_or_create(self, filters: dict, values: dict):
        """
        Обновляет объект, если найден. Иначе — создаёт новый.

        :param filters: условия поиска (например, {"email": "user@example.com"})
        :param values: данные для обновления или создания
        :return: (объект, created: bool)
        """
        async with new_session() as session:
            instance = await self.get_by(**filters)

            conditions = [getattr(self.model, key) == value for key, value in filters.items()]
            if instance:
                stmt = update(self.model).where(and_(*conditions)).values(**values).returning(self.model)
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
                result = await session.execute(select(self.model).where(and_(*conditions)))
                instance = result.scalar_one()
                return instance, False

    async def delete_by(self, **kwargs) -> int:
        async with new_session() as session:
            conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
            stmt = delete(self.model).where(and_(*conditions))
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def get_by_or(self, **kwargs):
        async with new_session() as session:
            conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
            stmt = select(self.model).where(or_(*conditions))
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    def _extract_unique_field_from_message(self, message: str) -> str | None:
        """
        Универсальный парсер поля из UNIQUE ошибки для SQLite/PostgreSQL/MySQL.
        Возвращает имя поля, если удалось извлечь, иначе None.
        """
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


class S3Repository:
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
