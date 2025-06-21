from src.errors import UniqueConstraintViolation
from src.repository import AbstractRepository
from src.users.errors import UserAlreadyExistsError
from src.users.models import LingoplayUser
from src.users.schemas import UserCreate


class UsersService:
    def __init__(self, repository: AbstractRepository):
        self._repository = repository

    async def add(self, user: UserCreate) -> LingoplayUser:
        user_dict = user.model_dump()

        try:
            user = await self._repository.create_one(user_dict)
        except UniqueConstraintViolation as e:
            raise UserAlreadyExistsError(field=e.field, value=e.value) from e

        return user

    async def get(self, user_id: int) -> LingoplayUser | None:
        user = await self._repository.get_by(id=user_id)
        return user

    async def get_by_email(self, email: str) -> LingoplayUser | None:
        user = await self._repository.get_by(email=email)
        return user
