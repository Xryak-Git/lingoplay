from pydantic import BaseModel, EmailStr, field_validator

from src.auth.models import hash_password
from src.models import PrimaryKey


class UserRead(BaseModel):
    """Pydantic model for reading user data."""

    id: PrimaryKey
    email: EmailStr

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str | None = None

    @field_validator("password", mode="before")
    @classmethod
    def hash(cls, v):
        """Hash the password before storing."""
        return hash_password(str(v))


class UserLogin(BaseModel):
    """Pydantic model for user login data."""

    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def email_required(cls, v):
        """Ensure the email field is not empty."""
        if not v:
            raise ValueError("Must not be empty string and must be a email")
        return v

    @field_validator("password")
    @classmethod
    def password_required(cls, v):
        """Ensure the password field is not empty."""
        if not v:
            raise ValueError("Must not be empty string")
        return v


class UserLoginResponse(BaseModel):
    """Pydantic model for the response after user login."""

    token: str | None = None
    user: UserRead
