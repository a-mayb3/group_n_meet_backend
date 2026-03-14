from pydantic import BaseModel

class RSVPBase(BaseModel):

    user_id: str
    event_id: str
    reserved_at: str
    is_cancelled: bool

class RSVPCreate(BaseModel):
    user_id: str
    event_id: str

