# src/crud/user.py

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException

from src import config
from src.auth.models import UserTokens
from src.repository import AlchemyRepository
from src.users.models import (
    LingoplayUser,
)


class AuthService:
    def __init__(self, tokens_rep: AlchemyRepository, users_rep: AlchemyRepository):
        self._tokens_rep = tokens_rep
        self._users_rep = users_rep

    async def generate_tokens(self, user: LingoplayUser):
        now = datetime.now(timezone(timedelta(hours=3)))
        jwt_timedelta = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRES_MINUTES)
        refresh_timedelta = timedelta(minutes=config.JWT_REFRESH_TOKEN_EXPIRES_MINUTES)

        jwt_payload = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "exp": int((now + jwt_timedelta).timestamp()),
            "iat": int(now.timestamp()),
        }

        refresh_jwt_payload = jwt_payload.copy()
        refresh_jwt_payload["exp"] = int((now + refresh_timedelta).timestamp())

        access_jwt = jwt.encode(jwt_payload, config.JWT_SECRET_KEY, algorithm="HS256")
        refresh_jwt = jwt.encode(refresh_jwt_payload, config.REFRESH_SECRET_KEY, algorithm="HS256")

        return [access_jwt, refresh_jwt]

    async def save_token(self, user_id: int, refresh_token: str) -> UserTokens:
        user_token = await self._tokens_rep.update_or_create(
            filters={"user_id": user_id}, values={"refresh_token": refresh_token}
        )
        return user_token

    async def validate_refresh_token(self, token: str) -> dict:
        return await self._validate_token(token, config.REFRESH_SECRET_KEY)

    async def validate_access_token(self, token: str) -> dict:
        return await self._validate_token(token, config.JWT_SECRET_KEY)

    async def refresh_tokens(self, refresh_token: str) -> tuple[str, str, LingoplayUser]:
        user_data = await self.validate_refresh_token(refresh_token)

        db_token = await self._tokens_rep.get_by(refresh_token=refresh_token)
        if not db_token:
            raise HTTPException(status_code=401, detail="User not authorized") from None

        user = await self._users_rep.get_by(id=user_data.get("id"))
        access_token, refresh_token = await self.generate_tokens(user)

        await self.save_token(user.id, refresh_token)

        return access_token, refresh_token, user

    async def logout(self, refresh_token: str):
        await self._tokens_rep.delete_by(refresh_token=refresh_token)

    async def _validate_token(self, token: str, key: str):
        try:
            user_data = jwt.decode(token, key, algorithms=["HS256"])
            return user_data
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired") from None
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token") from None
