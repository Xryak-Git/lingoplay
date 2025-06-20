from fastapi import APIRouter

from src.auth.dependencies import CurrentUser
from src.auth.schemas import UserRead
from src.database.core import DbSession

router = APIRouter()


# Middlware на авторизацию добавить
@router.get("/{user_id}")
async def get_user(db_session: DbSession, current_user: CurrentUser) -> UserRead:
    """Get a user."""
    # user = await get(db_session=db_session, user_id=user_id)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail=[{"msg": "A user with this id does not exist."}],
    #     )
    print(current_user)
    return current_user
