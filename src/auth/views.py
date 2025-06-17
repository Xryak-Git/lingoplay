from fastapi import APIRouter, HTTPException, status

from src.auth.schemas import UserCreate, UserRead
from src.auth.service import create, get, get_by_email
from src.database.core import DbSession
from src.models import PrimaryKey

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


@router.get("/{user_id}", response_model=UserRead)
async def get_user(db_session: DbSession, user_id: PrimaryKey):
    """Get a user."""
    user = await get(db_session=db_session, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=[{"msg": "A user with this id does not exist."}],
        )

    return user
