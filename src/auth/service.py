# src/crud/user.py

from datetime import datetime, timedelta, timezone
import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import (
    JWT_ACCESS_TOKEN_EXPIRES_MINUTES,
    JWT_REFRESH_TOKEN_EXPIRES_MINUTES,
    JWT_SECRET_KEY,
    REFRESH_SECRET_KEY,
    LingoplayUser,
    UserTokens,
)
from src.auth.schemas import UserCreate


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
        email=user_in.email, username=user_in.username, password=password
    )
    db_session.add(user)
    try:
        await db_session.commit()
        await db_session.refresh(user)
        return user
    except IntegrityError:
        await db_session.rollback()
        raise ValueError("User with this email or username already exists")


async def generate_tokens(user: LingoplayUser):
    now = datetime.now(timezone(timedelta(hours=3)))
    jwt_timedelta = timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
    refresh_timedelta = timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRES_MINUTES)

    jwt_payload = {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "exp": int((now + jwt_timedelta).timestamp()),
        "iat": int(now.timestamp()),
    }

    refresh_jwt_payload = jwt_payload.copy()
    refresh_jwt_payload["exp"] = int((now + refresh_timedelta).timestamp())

    access_jwt = jwt.encode(jwt_payload, JWT_SECRET_KEY, algorithm="HS256")
    refresh_jwt = jwt.encode(refresh_jwt_payload, REFRESH_SECRET_KEY, algorithm="HS256")

    return [access_jwt, refresh_jwt]


async def save_token(db_session: AsyncSession, user_id: int, refresh_token: str):
    stmt = select(UserTokens).where(UserTokens.user_id == user_id)
    result = await db_session.execute(stmt)

    user_token = result.scalar_one_or_none()
    if user_token:
        user_token.refresh_token = refresh_token
    else:
        user_token = UserTokens(
            user_id=user_id,
            refresh_token=refresh_token,
        )
        db_session.add(user_token)

    await db_session.commit()
    await db_session.refresh(user_token)
    return user_token
