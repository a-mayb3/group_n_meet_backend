from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr, PastDatetime
from typing import Optional

class UserBase(BaseModel):
    """
    Base model for users.
    """

    id: UUID
    email_address: EmailStr
    display_name: str
    user_type: str
    created: PastDatetime

class UserAuth(BaseModel):
    """
    Info sent by the client when logging in.
    """

    email_address: EmailStr
    password: SecretStr


class UserSearchParameters(BaseModel):
    """
    Query parameters for searching users.
    """

    q: str | None = None


class UserCreate(BaseModel):
    """
    User info sent by the client when creating a new user.
    """

    email_address: EmailStr
    display_name: str
    password: SecretStr


class UserUpdate(BaseModel):
    """
    User info sent by the client when updating an existing user.
    """

    email_address: Optional[EmailStr]
    display_name: Optional[str]

class UserPasswordUpdate(BaseModel):
    """
    User password update info sent by the client when updating an existing user's password.
    """

    current_password: SecretStr
    new_password: SecretStr
    confirm_new_password: SecretStr