from pydantic import BaseModel, EmailStr, field_validator

from src.models import PrimaryKey
from src.users.models import hash_password


class UserRead(BaseModel):
    """Pydantic model for reading user data."""

    id: PrimaryKey
    email: EmailStr

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str | None = None

    @field_validator("password", mode="before")
    @classmethod
    def hash(cls, v):
        """Hash the password before storing."""
        return hash_password(str(v))
