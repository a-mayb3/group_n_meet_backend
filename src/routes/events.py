import logging
from typing import List, Optional
from urllib import request
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
import utils

from schemas.organizer_group import OrganizerGroupSchema
from schemas.event import EventSchema

from models.events import EventBase, EventSearchParameters

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/events",
    tags=["events"],
)

@router.get("/{event_id}", response_model=EventBase)
def read_event(event_id: str, db: Session = Depends(get_db)):

    try:
        event_id_uuid: UUID = UUID(event_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event ID format")
    
    event = db.query(EventSchema).filter(EventSchema.id == event_id_uuid).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.get("/search", response_model=List[EventBase])
def search_events(params: EventSearchParameters = Depends(), db: Session = Depends(get_db)):
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

@router.post("/{event_id}/add_me")
def add_me_to_event(
    event_id: str,
    request: Request,
    db: Session = Depends(get_db),
    ):

    user = utils.get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    try:
        event_id_uuid: UUID = UUID(event_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid event ID format")

    event = db.query(EventSchema).filter(EventSchema.id == event_id_uuid).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    logger.debug(f"Adding user {user.id} to event {event_id_uuid}")
