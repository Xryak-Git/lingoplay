# src/crud/user.py

from src.auth.models import LingoplayUser
from src.auth.schemas import UserCreate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError


async def get(*, db_session: AsyncSession, user_id: int) -> LingoplayUser | None:
    stmt = select(LingoplayUser).where(LingoplayUser.id == user_id)
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()


async def get_by_email(*, db_session: AsyncSession, email: str) -> LingoplayUser | None:
    stmt = select(LingoplayUser).where(LingoplayUser.email == email)
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()


async def create(db_session: AsyncSession, user_in: UserCreate) -> LingoplayUser:
    password = bytes(user_in.password, "utf-8")
    user = LingoplayUser(
        email=user_in.email,
        username=user_in.username,
        password=password
    )
    db_session.add(user)
    try:
        await db_session.commit()
        await db_session.refresh(user)
        return user
    except IntegrityError:
        await db_session.rollback()
        raise ValueError("User with this email or username already exists")
