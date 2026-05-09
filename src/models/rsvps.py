from pydantic import BaseModel, StrictBool, PastDatetime
from uuid import UUID


class RSVPBase(BaseModel):

    user_id: UUID
    event_id: UUID
    reserved_at: PastDatetime
    is_cancelled: StrictBool = False

class RSVPCreate(BaseModel):
    user_id: UUID
    event_id: UUID
