from fastapi import APIRouter, HTTPException, Response, status

from src.auth.schemas import UserCreate, UserLogin, UserLoginResponse
from src.auth.service import create, generate_tokens, get_by_email, save_token
from src.database.core import DbSession
from src.users.schemas import UserRead

router = APIRouter()


@router.post(
    "",
    response_model=UserRead,
)
async def create_user(
    user_in: UserCreate,
    db_session: DbSession,
):
    """Creates a new user."""
    user = await get_by_email(db_session=db_session, email=user_in.email)

    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"email": "A user with this email already exists."},
        )

    user = await create(db_session=db_session, user_in=user_in)
    return user


@router.post("/login", response_model=UserLoginResponse)
async def login(
    user_login: UserLogin,
    response: Response,
    db_session: DbSession,
):
    user = await get_by_email(db_session=db_session, email=user_login.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this email does not exist."}],
        )

    if user.verify_password(user_login.password):
        jwt_token, refresh_token = await generate_tokens(user)
        await save_token(db_session=db_session, user_id=user.id, refresh_token=refresh_token)
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
