import logging
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, Query
from pydantic import NaiveDatetime
from sqlalchemy.orm import Session

from database import get_db
import utils

from schemas.organizer_group import OrganizerGroupSchema
from schemas.event import EventSchema
from schemas.reservation import reservation

from models.events import (
    EventBase,
    EventCreate,
    EventDescriptionGenerateRequest,
    EventDescriptionGenerateResponse,
    EventSearchParameters,
    EventUpdate,
)
from services.event_description import generate_event_description

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/events",
    tags=["events"],
)

def get_event_search_params(
    name: Optional[str] = Query(None),
    organizer_group_name: Optional[str] = Query(None),
    place: Optional[str] = Query(None),
    start_time_from: Optional[NaiveDatetime] = Query(None),
    start_time_to: Optional[NaiveDatetime] = Query(None),
    end_time_from: Optional[NaiveDatetime] = Query(None),
    end_time_to: Optional[NaiveDatetime] = Query(None),
) -> EventSearchParameters:
    return EventSearchParameters(
        name=name,
        organizer_group_name=organizer_group_name,
        place=place,
        start_time_from=start_time_from,
        start_time_to=start_time_to,
        end_time_from=end_time_from,
        end_time_to=end_time_to,
    )

@router.get("/search", response_model=List[EventBase])
def search_events(
    params: EventSearchParameters = Depends(get_event_search_params),
    db: Session = Depends(get_db)
    ):
    
    query = db.query(EventSchema)

    if params is None:
        raise HTTPException(status_code=400, detail="Invalid query parameters")

    if params.name:
        query = query.filter(EventSchema.name.ilike(f"%{params.name}%"))
    
    if params.organizer_group_name:
        query = query.join(OrganizerGroupSchema).filter(OrganizerGroupSchema.name.ilike(f"%{params.organizer_group_name}%"))
    
    if params.place:
        query = query.filter(EventSchema.place == params.place)
    
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

@router.delete("/{event_id}/cancel")
def cancel_event(
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

    organizerGroup = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == event.organizer_group_id).first()

    if not organizerGroup:
        raise HTTPException(status_code=400, detail="Invalid organizer group ID")

    if event not in organizerGroup.events:
        raise HTTPException(status_code=400, detail="Event does not belong to the organizer group")

    if user not in organizerGroup.members:
        raise HTTPException(status_code=403, detail="User is not a member of the organizer group")

    db.query(EventSchema).filter(EventSchema.id == event_id_uuid).update(
        {EventSchema.is_cancelled: True},
        synchronize_session=False,
    )
    db.commit()

    logger.debug(f"Cancelling event {event_id_uuid} by user {user.id}")
    return {"message": "Event cancelled successfully"}

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
    
    new_id = uuid4()
    new_rsvp = reservation.insert().values(
        id=new_id,
        user_id=user.id,
        event_id=event_id_uuid,
        is_cancelled=False
    )
    db.execute(new_rsvp)
    db.commit()
    
    logger.debug(f"Adding user {user.id} to event {event_id_uuid}")
    return {"id": str(new_id), "user_id": str(user.id), "event_id": str(event_id_uuid)}

@router.delete("/{event_id}/remove_me")
def remove_me_from_event(
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

    cancel_rsvp = reservation.update().where(
        (reservation.c.user_id == user.id) &
        (reservation.c.event_id == event_id_uuid)
    ).values(is_cancelled=True)
    db.execute(cancel_rsvp)
    db.commit()
    
    logger.debug(f"Removing user {user.id} from event {event_id_uuid}")
    return {"message": "Event RSVP cancelled successfully"}

@router.post("/")
def create_event(
    event: EventCreate,
    request: Request,
    db: Session = Depends(get_db),
    ):

    user = utils.get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")


    organizerGroup = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == event.organizer_group_id).first()

    if not organizerGroup:
        raise HTTPException(status_code=400, detail="Invalid organizer group ID")

    if user not in organizerGroup.members:
        raise HTTPException(status_code=403, detail="User is not a member of the organizer group")

    new_event = EventSchema(**event.model_dump())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)

    logger.debug(f"Creating event {event.name} by user {user.id}")
    return new_event


@router.post("/generate-description", response_model=EventDescriptionGenerateResponse)
def generate_description_for_event(
    request_body: EventDescriptionGenerateRequest,
    request: Request,
    db: Session = Depends(get_db),
):

    user = utils.get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    suggested_description = generate_event_description(request_body, db)

    logger.debug(
        "Generating event description for user %s and event %s",
        user.id,
        request_body.event_name,
    )
    return {"suggested_description": suggested_description}

@router.put("/{event_id}")
def update_event(
    event_id: str,
    event_update: EventUpdate,
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

    organizerGroup = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == event.organizer_group_id).first()

    if not organizerGroup:
        raise HTTPException(status_code=400, detail="Invalid organizer group ID")

    if user not in organizerGroup.members:
        raise HTTPException(status_code=403, detail="User is not a member of the organizer group")

    for key, value in event_update.model_dump().items():
        setattr(event, key, value)

    db.commit()
    
    logger.debug(f"Updating event {event.name} by user {user.id}")

    return event
