from fastapi import APIRouter

from src.auth.dependencies import CurrentUser
from src.auth.schemas import UserRead
from src.database.core import DbSession


router = APIRouter()


@router.get("/current")
async def current_user(db_session: DbSession, current_user: CurrentUser) -> UserRead:
    """Get a user."""
    return current_user
