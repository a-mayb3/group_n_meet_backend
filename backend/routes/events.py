from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base
from typing import List, Optional
from database import get_db
from schemas.organizer_group import OrganizerGroup

Base = declarative_base()

"""SQLAlchemy ORM model for an event"""
class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)
    start_time = Column(String, nullable=True)
    end_time = Column(String, nullable=True)
    place = Column(String, nullable=True)
    organizer_group_id = Column(String)

"""Base model for an event"""
class EventBase(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    place: Optional[str] = None
    organizer_group_id: str

"""Query parameters for searching events"""
class EventQueryParams(BaseModel):
    name: Optional[str] = None
    organizer_group_name: Optional[str] = None
    places: Optional[List[str]] = None
    start_time_from: Optional[str] = None
    start_time_to: Optional[str] = None
    end_time_from: Optional[str] = None
    end_time_to: Optional[str] = None



router = APIRouter(
    prefix="/events",
    tags=["events"],
)

@router.get("/", response_model=List[EventBase])
def read_events(db: Session = Depends(get_db)):
    events = db.query(Event).all()
    return events

@router.get("/search", response_model=List[EventBase])
def search_events(params: EventQueryParams = Depends(), db: Session = Depends(get_db)):
    query = db.query(Event)

    if params.name:
        query = query.filter(Event.name.ilike(f"%{params.name}%"))
    
    if params.organizer_group_name:
        query = query.join(OrganizerGroup).filter(OrganizerGroup.name.ilike(f"%{params.organizer_group_name}%"))
    
    if params.places:
        query = query.filter(Event.place.in_(params.places))
    
    if params.start_time_from is not None:
        query = query.filter(Event.start_time >= params.start_time_from)
    
    if params.start_time_to is not None:
        query = query.filter(Event.start_time <= params.start_time_to)
    
    if params.end_time_from is not None:
        query = query.filter(Event.end_time >= params.end_time_from)
    
    if params.end_time_to is not None:
        query = query.filter(Event.end_time <= params.end_time_to)

    events = query.all()
    return events
