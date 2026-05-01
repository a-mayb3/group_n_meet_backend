import datetime

from pydantic import BaseModel, EmailStr, SecretStr, UUID7
from typing import List, Optional

from models.rsvps import RSVPBase

class UserBase(BaseModel):
    """
    Base model for users.
    """
    
    id: UUID7
    email_address: EmailStr
    display_name: str
    user_type: str
    created: datetime.datetime

class FullUser(UserBase):
    """
    User model with all fields.
    """
    
    rsvps: List[RSVPBase] = []
    organizer_groups: List[UUID7] = []


## Mainly used from requests

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