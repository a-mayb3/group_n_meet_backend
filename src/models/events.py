from typing import List, Optional
from pydantic import BaseModel

class EventBase(BaseModel):
    
    id: str
    name: str
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    place: Optional[str] = None
    organizer_group_id: str

class EventQueryParams(BaseModel):
    """Query parameters for searching events"""

    name: Optional[str] = None
    organizer_group_name: Optional[str] = None
    places: Optional[List[str]] = None
    start_time_from: Optional[str] = None
    start_time_to: Optional[str] = None
    end_time_from: Optional[str] = None
    end_time_to: Optional[str] = None