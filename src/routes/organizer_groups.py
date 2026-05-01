import logging
from urllib import request

from pydantic import UUID7

from schemas.organizer_group import OrganizerGroupSchema
from schemas.event import EventSchema

from models.organizer_groups import OrganizerGroupBase, OrganizerGroupCreate
from models.events import EventBase

from typing import List

from database import get_db
from utils import get_user_from_jwt

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/org",
    tags=["organizer_groups"],
)

@router.post("/", response_model=OrganizerGroupBase)
def create_organizer_group(group: OrganizerGroupCreate, request: Request, db: Session = Depends(get_db)):

    user = get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    logger.debug(f"Creating organizer group {group.name} by user {user.id}")

    new_group : OrganizerGroupSchema = OrganizerGroupSchema(
        **group.model_dump(),
        members=[user]
    )

    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    return OrganizerGroupBase.model_validate(new_group)

@router.get("/{id}", response_model=OrganizerGroupBase)
def get_organizer_group(id: str, request: Request, db: Session = Depends(get_db)):
    """Get an organizer group by its ID."""

    logger.debug(f"Getting organizer group {id} by {request.client}")

    group = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")
    
    return OrganizerGroupBase.model_validate(group)

@router.get("/{id}/events", response_model=list[EventBase])
def get_organizer_group_events(id: str, request: Request, db: Session = Depends(get_db)):
    """Get events organized by a specific organizer group."""

    logger.debug(f"Getting events for organizer group {id} by {request.client}")

    group = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")
    
    return [EventBase.model_validate(event) for event in group.events]

@router.delete("/{id}")
def delete_organizer_group(id: UUID7, request: Request, db: Session = Depends(get_db)):
    """Delete an organizer group by its ID."""

    logger.debug(f"Deleting organizer group {id} by {request.client}")

    user = get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    group = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")
    
    if user not in group.members:
        raise HTTPException(status_code=403, detail="Forbidden: You are not a member of this organizer group")

    db.delete(group)
    db.commit()

    return {"message": "Organizer group deleted successfully"}

@router.delete("/leave")
def leave_organizer_group(group_id: UUID7, request: Request, db: Session = Depends(get_db)):
    """Leave an organizer group."""

    logger.debug(f"Leaving organizer group {group_id} by {request.client}")

    user = get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    group = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == group_id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")
    
    if user not in group.members:
        raise HTTPException(status_code=403, detail="Forbidden: You are not a member of this organizer group")

    if len(group.members) <= 1:
        raise HTTPException(status_code=400, detail="Cannot leave organizer group: You are the only member. Please delete the group instead.")

    group.members.remove(user)
    db.commit()

    return {"message": "Left organizer group successfully"}