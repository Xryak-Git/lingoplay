from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from src.auth.dependencies import CurrentUser
from src.users.dependencies import user_service
from src.users.errors import UserAlreadyExistsError
from src.users.schemas import UserCreate, UserRead
from src.users.service import UsersService

router = APIRouter()


@router.post("/")
async def create_user(user_in: UserCreate, user_service: Annotated[UsersService, Depends(user_service)]) -> UserRead:
    """Creates a new user."""
    try:
        user = await user_service.add(user_in)
        return user
    except UserAlreadyExistsError as e:
        raise HTTPException(
            status_code=409,
            detail=[{"msg": f"{e.field} '{e.value}' already exists."}],
        ) from e


@router.get("/current")
async def current_user(current_user: CurrentUser) -> UserRead:
    """Get a user."""
    return current_user
