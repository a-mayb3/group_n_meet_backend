from pydantic import BaseModel, EmailStr
from typing import List

from models.rsvps import RSVPBase

class UserBase(BaseModel):
    id: str
    email_address: EmailStr
    display_name: str
    user_type: str # REGULAR or ADMIN

class UserFullInfo(UserBase):
    """Includes all user information, including RSVPs. This is what is returned by the API when fetching user information."""
    rsvps: List[RSVPBase] = []

class UserAuth(BaseModel):
    """Info sent by the client when logging in."""
    email_address: EmailStr
    password: str
