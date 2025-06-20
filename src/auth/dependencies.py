from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src import config
from src.auth.service import get as get_user
from src.database.core import DbSession
from src.users.models import LingoplayUser

security = HTTPBearer()


async def get_current_user(
    db_session: DbSession, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> LingoplayUser:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=["HS256"])
        return await get_user(db_session=db_session, user_id=payload.get("id"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired") from None
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token") from None


CurrentUser = Annotated[LingoplayUser, Depends(get_current_user)]
