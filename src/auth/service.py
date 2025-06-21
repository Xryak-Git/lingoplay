# src/crud/user.py

from datetime import datetime, timedelta, timezone

import jwt

from src import config
from src.auth.models import UserTokens
from src.repository import AlchemyRepository
from src.users.models import (
    LingoplayUser,
)


class AuthService:
    def __init__(self, repository: AlchemyRepository):
        self._repository = repository

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
        user_token = self._repository.update_or_create(
            filters={"user_id": user_id}, values={"refresh_token": refresh_token}
        )
        return user_token
