from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from src.auth.service import get as get_user
from src.database.core import DbSession
from src.users.models import JWT_SECRET_KEY, LingoplayUser

security = HTTPBearer()


async def get_current_user(
    db_session: DbSession, credentials: HTTPAuthorizationCredentials = Depends(security)
) -> LingoplayUser:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
        return await get_user(db_session=db_session, user_id=payload.get("id"))
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


CurrentUser = Annotated[LingoplayUser, Depends(get_current_user)]
