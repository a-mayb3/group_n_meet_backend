from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, NaiveDatetime, StrictBool

class EventBase(BaseModel):

    id: UUID
    name: str
    description: Optional[str] = None
    start_time: Optional[NaiveDatetime] = None
    end_time: Optional[NaiveDatetime] = None
    place: Optional[str] = None
    organizer_group_id: UUID
    is_cancelled: StrictBool = False


class EventSearchParameters(BaseModel):

    name: Optional[str] = None
    organizer_group_name: Optional[str] = None
    place: Optional[str] = None
    start_time_from: Optional[NaiveDatetime] = None
    start_time_to: Optional[NaiveDatetime] = None
    end_time_from: Optional[NaiveDatetime] = None
    end_time_to: Optional[NaiveDatetime] = None

class EventCreate(BaseModel):

    name: str
    description: Optional[str] = None
    start_time: Optional[NaiveDatetime] = None
    end_time: Optional[NaiveDatetime] = None
    place: Optional[str] = None
    organizer_group_id: UUID


class EventDescriptionGenerateRequest(BaseModel):

    existing_description: str
    event_name: Optional[str] = None
    start_time: Optional[NaiveDatetime] = None
    end_time: Optional[NaiveDatetime] = None
    place: Optional[str] = None
    organizer_group_id: Optional[UUID] = None


class EventDescriptionGenerateResponse(BaseModel):

    suggested_description: str

class EventUpdate(BaseModel):

    name: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[NaiveDatetime] = None
    end_time: Optional[NaiveDatetime] = None
    place: Optional[str] = None