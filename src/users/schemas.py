from pydantic import BaseModel, EmailStr

from src.models import PrimaryKey


class UserRead(BaseModel):
    """Pydantic model for reading user data."""

    id: PrimaryKey
    email: EmailStr

    model_config = {"from_attributes": True}
