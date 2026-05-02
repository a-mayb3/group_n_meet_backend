from uuid import UUID

from pydantic import BaseModel, EmailStr, SecretStr, PastDatetime
from typing import Optional

class UserBase(BaseModel):
    id: UUID
    email_address: EmailStr
    display_name: str
    user_type: str
    created: PastDatetime

class UserAuth(BaseModel):
    email_address: EmailStr
    password: SecretStr


class UserSearchParameters(BaseModel):
    q: str = ""


class UserCreate(BaseModel):
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