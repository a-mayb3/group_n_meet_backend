from pydantic import BaseModel, UUID7, StrictBool

class RSVPBase(BaseModel):

    user_id: UUID7
    event_id: UUID7
    reserved_at: str
    is_cancelled: StrictBool = False

class RSVPCreate(BaseModel):
    user_id: UUID7
    event_id: UUID7
