from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.auth.dependencies import auth_service
from src.auth.schemas import UserLogin, UserLoginResponse
from src.auth.service import AuthService
from src.users.dependencies import user_service
from src.users.schemas import UserRead
from src.users.service import UsersService

router = APIRouter()


@router.post("/login")
async def login(
    user_login: UserLogin,
    response: Response,
    auth_service: Annotated[AuthService, Depends(auth_service)],
    user_service: Annotated[UsersService, Depends(user_service)],
) -> UserLoginResponse:
    user = await user_service.get_by_email(email=user_login.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this email does not exist."}],
        )

    if user.verify_password(user_login.password):
        jwt_token, refresh_token = await auth_service.generate_tokens(user)
        await auth_service.save_token(user_id=user.id, refresh_token=refresh_token)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            max_age=3600,
        )
        return {"token": jwt_token, "user": UserRead.model_validate(user)}

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=[{"msg": "Password is wrong"}],
    )
