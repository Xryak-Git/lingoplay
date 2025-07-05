import re
from abc import ABC, abstractmethod
from functools import wraps
from typing import overload

from sqlalchemy import delete, exists, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import Base
from src.errors import DatabaseCommitError, UniqueConstraintViolation


class AbstractRepository(ABC):
    @abstractmethod
    async def filter():
        raise NotImplementedError

    @abstractmethod
    async def filter_or_():
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

    async def filter(self, first: bool = False, **kwargs) -> list[Base] | Base | None:
        async with self._session as session:
            stmt = select(self.model).filter_by(**kwargs)
            result = await session.execute(stmt)
            return result.scalars().first() if first else result.scalars().all()

    async def filter_or_(self, first: bool = False, **kwargs) -> list[Base] | Base | None:
        async with self._session as session:
            conditions = [getattr(self.model, key) == value for key, value in kwargs.items()]
            stmt = select(self.model).where(or_(*conditions))
            result = await session.execute(stmt)
            return result.scalars().first() if first else result.scalars().all()

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

    async def update_by(self, **kwargs) -> int:
        async with self._session as session:
            stmt = update(self.model).filter_by(**kwargs)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount

    async def update_or_create(self, filters: dict, values: dict):
        async with self._session as session:
            instance = await self.filter(**filters, first=True)

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
