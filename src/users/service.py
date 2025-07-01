from src.errors import UniqueConstraintViolation
from src.repository import AbstractRepository
from src.users.errors import UserAlreadyExistsError
from src.users.models import LingoplayUsers
from src.users.schemas import UserCreate


class UsersService:
    def __init__(self, repository: AbstractRepository):
        self._repository = repository

    async def add(self, user: UserCreate) -> LingoplayUsers:
        user_dict = user.model_dump()

        try:
            user = await self._repository.create_one(user_dict)
        except UniqueConstraintViolation as e:
            raise UserAlreadyExistsError(field=e.field, value=e.value) from e

        return user

    async def get(self, user_id: int) -> LingoplayUsers | None:
        user = await self._repository.filter(id=user_id, first=True)
        return user

    async def get_by_email(self, email: str) -> LingoplayUsers | None:
        user = await self._repository.filter(email=email, first=True)
        return user

    async def exists(self, **kwargs) -> bool:
        user = await self._repository.filter_or_(**kwargs, first=True)
        return user is not None
