import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, PastDatetime

from models.users import UserBase

class OrganizerGroupBase(BaseModel):

    id: UUID
    name: str
    description: Optional[str] = None
    members:  list[UserBase] = []
    created: PastDatetime

class OrganizerGroupCreate(BaseModel):

    name: str
    description: Optional[str] = None

class OrganizerGroupUpdate(BaseModel):

    name: Optional[str] = None
    description: Optional[str] = None
class OrganizerGroupSearchParameters(BaseModel):
    q: Optional[str] = None
