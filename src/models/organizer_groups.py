import datetime
from pydantic import BaseModel, UUID7

class OrganizerGroupBase(BaseModel):

    id: UUID7
    name: str
    description: str
    created: datetime.datetime

class OrganizerGroupCreate(BaseModel):

    name: str
    description: str

class OrganizerGroupSearchParameters(BaseModel):
    q: str | None = None
