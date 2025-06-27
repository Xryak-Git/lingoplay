from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException as StarletteHTTPException

from src import config
from src.auth.repository import AuthRepository
from src.auth.service import AuthService
from src.database.core import get_session
from src.users.dependencies import user_service
from src.users.models import LingoplayUser
from src.users.repository import UserRepository
from src.users.service import UsersService


class CustomHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials:
        try:
            return await super().__call__(request)
        except StarletteHTTPException as e:
            if e.status_code == 403:
                raise HTTPException(status_code=401, detail="Not authenticated") from e
            raise e


security = CustomHTTPBearer()


async def auth_service(session: Annotated[AsyncSession, Depends(get_session)]):
    return AuthService(AuthRepository(session), UserRepository(session))


async def get_current_user(
    user_service: Annotated[UsersService, Depends(user_service)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> LingoplayUser:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
        return await user_service.get(user_id=payload.get("id"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token") from None


CurrentUser = Annotated[LingoplayUser, Depends(get_current_user)]
