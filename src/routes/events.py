from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column, String
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

from database import get_db

from schemas.organizer_group import OrganizerGroupSchema
from schemas.event import EventSchema

from models.events import EventBase, EventQueryParams

Base = declarative_base()

router = APIRouter(
    prefix="/events",
    tags=["events"],
)

@router.get("/", response_model=List[EventBase])
def read_events(db: Session = Depends(get_db)):
    events = db.query(EventSchema).all()
    return events

@router.get("/search", response_model=List[EventBase])
def search_events(params: EventQueryParams = Depends(), db: Session = Depends(get_db)):
    query = db.query(EventSchema)

    if params is None:
        raise HTTPException(status_code=400, detail="Invalid query parameters")

    if params.name:
        query = query.filter(EventSchema.name.ilike(f"%{params.name}%"))
    
    if params.organizer_group_name:
        query = query.join(OrganizerGroupSchema).filter(OrganizerGroupSchema.name.ilike(f"%{params.organizer_group_name}%"))
    
    if params.places:
        query = query.filter(EventSchema.place.in_(params.places))
    
    if params.start_time_from is not None:
        query = query.filter(EventSchema.start_time >= params.start_time_from)
    
    if params.start_time_to is not None:
        query = query.filter(EventSchema.start_time <= params.start_time_to)
    
    if params.end_time_from is not None:
        query = query.filter(EventSchema.end_time >= params.end_time_from)
    
    if params.end_time_to is not None:
        query = query.filter(EventSchema.end_time <= params.end_time_to)

    events = query.all()
    return events
