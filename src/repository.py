from abc import ABC, abstractmethod

from aiosqlite import IntegrityError
from sqlalchemy import and_, insert, select, update

from src.database.core import new_session


class AbstractRepository(ABC):
    @abstractmethod
    async def get_by():
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
            stmt = insert(self.model).values(**data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

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
            instance = self.get_by(*filters)

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
