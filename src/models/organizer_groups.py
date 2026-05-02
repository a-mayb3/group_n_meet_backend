import datetime
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


class OrganizerGroupSearchParameters(BaseModel):
    q: str | None = None
