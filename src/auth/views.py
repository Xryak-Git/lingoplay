from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import auth_service
from src.auth.service import AuthService
from src.users.dependencies import user_service
from src.users.schemas import UserCreate, UserLogin, UserLoginResponse, UserRead
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
            key="refresh_token",
            value=refresh_token,
            max_age=3600,
            httponly=True,
            path="/",
            samesite="lax",
        )

        return {"token": jwt_token, "user": UserRead.model_validate(user)}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=[{"msg": "Password is wrong"}],
    )


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(auth_service)],
) -> UserLoginResponse:
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=[{"msg": "no refresh token"}])
    access_token, refresh_token, user = await auth_service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=3600,
        httponly=True,
        path="/",
        samesite="lax",
    )

    return {"token": access_token, "user": UserRead.model_validate(user)}


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    auth_service: Annotated[AuthService, Depends(auth_service)],
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=[{"msg": "user is not authorized"}])
    await auth_service.logout(refresh_token)

    response.delete_cookie(key="refresh_token")
    return {"detail": "Logged out"}


@router.post("/registrate")
async def registrate(
    user_create: UserCreate,
    user_service: Annotated[UsersService, Depends(user_service)],
) -> JSONResponse:
    user = await user_service.exists(username=user_create.username, email=user_create.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=[{"msg": "A user with this email or username already exists"}],
        )

    user = await user_service.add(user_create)

    return JSONResponse(status_code=201, content={"message": "User registered successfully"})
