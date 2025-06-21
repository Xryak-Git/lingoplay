from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.dependencies import CurrentUser
from src.users.dependencies import user_service
from src.users.schemas import UserCreate, UserRead
from src.users.service import UsersService

router = APIRouter()


@router.post("")
async def create_user(user_in: UserCreate, user_service: Annotated[UsersService, Depends(user_service)]) -> UserRead:
    """Creates a new user."""
    user = await user_service.add(user_in)
    return user


@router.get("/current")
async def current_user(current_user: CurrentUser) -> UserRead:
    """Get a user."""
    return current_user
