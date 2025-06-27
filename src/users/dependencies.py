from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.core import get_session
from src.users.repository import UserRepository
from src.users.service import UsersService


async def user_service(session: Annotated[AsyncSession, Depends(get_session)]):
    return UsersService(repository=UserRepository(session=session))
