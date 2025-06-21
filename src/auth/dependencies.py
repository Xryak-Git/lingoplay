from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src import config
from src.auth.repository import AuthRepository
from src.auth.service import AuthService
from src.users.dependencies import user_service
from src.users.models import LingoplayUser
from src.users.repository import UserRepository
from src.users.service import UsersService

security = HTTPBearer()


def auth_service():
    return AuthService(AuthRepository(), UserRepository())


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
