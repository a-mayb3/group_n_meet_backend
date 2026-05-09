import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, PastDatetime

class OrganizerGroupBase(BaseModel):

    id: UUID
    name: str
    description: str
    created: PastDatetime

class OrganizerGroupCreate(BaseModel):

    name: str
    description: str

class OrganizerGroupUpdate(BaseModel):

    name: Optional[str] = None
    description: Optional[str] = None
class OrganizerGroupSearchParameters(BaseModel):
    q: Optional[str] = None
