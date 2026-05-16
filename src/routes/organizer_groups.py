import logging
from urllib import request
from datetime import datetime, timezone

from uuid import UUID

from models.users import UserBase
from schemas.organizer_group import OrganizerGroupSchema
from schemas.event import EventSchema

from models.organizer_groups import OrganizerGroupBase, OrganizerGroupCreate, OrganizerGroupUpdate
from models.events import EventBase

from typing import List

from database import get_db
from utils import get_user_from_jwt

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/org",
    tags=["organizer_groups"],
)


@router.post("/", response_model=OrganizerGroupBase)
def create_organizer_group(
    group: OrganizerGroupCreate, request: Request, db: Session = Depends(get_db)
):

    user = get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    logger.debug(f"Creating organizer group {group.name} by user {user.id}")

    new_group: OrganizerGroupSchema = OrganizerGroupSchema(
        **group.model_dump(),
        created_at=datetime.now(timezone.utc)
    )
    new_group.members.append(user)

    # Prevent duplicate group names when possible
    existing = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.name == group.name).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="Organizer group with that name already exists")

    try:
        db.add(new_group)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Organizer group with that name already exists")

    db.refresh(new_group)

    return OrganizerGroupBase.model_validate(
        {
            "id": new_group.id,
            "name": new_group.name,
            "description": new_group.description,
            "created": new_group.created_at,
        }
    )


@router.get("/{id}", response_model=OrganizerGroupBase)
def get_organizer_group(id: str, request: Request, db: Session = Depends(get_db)):
    """Get an organizer group by its ID."""

    logger.debug(f"Getting organizer group {id} by {request.client}")

    organizer_group: OrganizerGroupSchema = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == id).first()

    if not organizer_group:
        raise HTTPException(status_code=404, detail="Organizer group not found")

    return OrganizerGroupBase.model_validate(
        {
            "id": organizer_group.id,
            "name": organizer_group.name,
            "description": organizer_group.description,
            "created": organizer_group.created_at,
            "members": [
                UserBase.model_validate({
                    "id": member.id,
                    "email_address": member.email,
                    "display_name": member.display_name,
                    "user_type": member.user_type,
                    "created": member.created_at or datetime.now(timezone.utc),
                })
                for member in organizer_group.members
            ]
        }
    )


@router.get("/{id}/events", response_model=list[EventBase])
def get_organizer_group_events(
    id: str, request: Request, db: Session = Depends(get_db)
):
    """Get events organized by a specific organizer group."""

    logger.debug(f"Getting events for organizer group {id} by {request.client}")

    group = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")

    return [EventBase.model_validate(
        {
            "id": event.id,
            "name": event.name,
            "description": event.description,
            "start_time": event.start_time,
            "end_time": event.end_time,
            "place": event.place,
            "organizer_group_id": event.organizer_group_id,
        }
    ) for event in group.events]


@router.delete("/{id}")
def delete_organizer_group(id: UUID, request: Request, db: Session = Depends(get_db)):
    """Delete an organizer group by its ID."""

    logger.debug(f"Deleting organizer group {id} by {request.client}")

    user = get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    group = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")

    if user not in group.members:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You are not a member of this organizer group",
        )

    if len(group.members) > 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete organizer group: There are other members in the group. Please remove all members before deleting the group.",
        )

    db.delete(group)
    db.commit()

    return {"message": "Organizer group deleted successfully"}


@router.delete("/{id}/leave")
def leave_organizer_group(
    id: UUID, request: Request, db: Session = Depends(get_db)
):
    """Leave an organizer group."""

    logger.debug(f"Leaving organizer group {id} by {request.client}")

    user = get_user_from_jwt(request, db)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    group = (
        db.query(OrganizerGroupSchema)
        .filter(OrganizerGroupSchema.id == id)
        .first()
    )

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")

    if user not in group.members:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You are not a member of this organizer group",
        )

    if len(group.members) <= 1:
        raise HTTPException(
            status_code=400,
            detail="Cannot leave organizer group: You are the only member. Please delete the group instead.",
        )

    group.members.remove(user)
    db.commit()

    return {"message": "Left organizer group successfully"}

@router.put("/{id}")
def update_organizer_group(
    id: UUID,
    group_update: OrganizerGroupUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    """Update an organizer group by its ID."""

    logger.debug(f"Updating organizer group {id} by {request.client}")

    user = get_user_from_jwt(request, db)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    group = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.id == id).first()

    if not group:
        raise HTTPException(status_code=404, detail="Organizer group not found")
    
    if user not in group.members:
        raise HTTPException(
            status_code=403,
            detail="Forbidden: You are not a member of this organizer group",
        )
    
    for key, value in group_update.model_dump().items():
        setattr(group, key, value)

        # If updating the name, make sure it's not already taken by another group
    if group_update.name:
        existing = db.query(OrganizerGroupSchema).filter(OrganizerGroupSchema.name == group_update.name).first()
        # Only raise if a different group has this name
        if existing is not None and existing != group:
            raise HTTPException(status_code=409, detail="Organizer group with that name already exists")

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Organizer group with that name already exists")

    db.refresh(group)

    return OrganizerGroupBase.model_validate(
        {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created": group.created_at,
        }
    )