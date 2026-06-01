import logging
from datetime import datetime, timezone

from typing import Any, cast

from schemas.user import UserSchema
from schemas.organizer_group import OrganizerGroupSchema, organizer_group_members
from schemas.reservation import reservation

from utils import get_user_from_jwt, renew_user_token

from models.users import UserBase, UserAuth, UserUpdate
from models.organizer_groups import OrganizerGroupBase
from models.rsvps import RSVPBase

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import delete, select
from sqlalchemy.orm import Session
from database import get_db

from pyargon2 import hash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/me", tags=["me"])


@router.get("/", response_model=UserBase)
def get_personal_info(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """
    Get logged-in user's profile information
    """
    user = get_user_from_jwt(request, db, response)

    return UserBase.model_validate(
        {
            "id": user.id,
            "email_address": user.email,
            "display_name": user.display_name,
            "user_type": user.user_type,
            "created": user.created_at or datetime.now(timezone.utc),
        }
    )


@router.get("/get_orgs", response_model=list[OrganizerGroupBase])
def get_my_organizer_groups(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """
    Get logged-in user's organizer groups
    """
    user = get_user_from_jwt(request, db, response)
    groups = (
        db.query(OrganizerGroupSchema)
        .join(
            organizer_group_members,
            OrganizerGroupSchema.id == organizer_group_members.c.organizer_group_id,
        )
        .filter(organizer_group_members.c.user_id == user.id)
        .all()
    )

    return [
        OrganizerGroupBase.model_validate(
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "created": group.created_at or datetime.now(timezone.utc),
            }
        )
        for group in groups
    ]


@router.get("/get_rsvps", response_model=list[RSVPBase])
def get_my_rsvps(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Get the current user's RSVPs.
    """
    user = get_user_from_jwt(request, db, response)
    rows = db.execute(
        select(
            reservation.c.user_id,
            reservation.c.event_id,
            reservation.c.reserved_at,
            reservation.c.is_cancelled,
        ).where(reservation.c.user_id == user.id)
    ).all()

    return [
        RSVPBase.model_validate(
            {
                "user_id": row.user_id,
                "event_id": row.event_id,
                "reserved_at": row.reserved_at,
                "is_cancelled": row.is_cancelled,
            }
        )
        for row in rows
    ]


@router.delete("/delete_me")
def delete_my_account(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """
    Delete the current user's account.
    """
    user = get_user_from_jwt(request, db, response)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    user_groups = (
        db.query(OrganizerGroupSchema)
        .join(
            organizer_group_members,
            OrganizerGroupSchema.id == organizer_group_members.c.organizer_group_id,
        )
        .filter(organizer_group_members.c.user_id == user.id)
        .all()
    )

    for group in user_groups:
        if len(group.members) <= 1:
            db.delete(group)
        else:
            group.members.remove(user)

    db.execute(delete(reservation).where(reservation.c.user_id == user.id))
    db.delete(user)
    db.commit()

    response.delete_cookie("access_token")

    return {"message": "Account deleted successfully"}


@router.put("/", response_model=UserBase)
def update_personal_info(
    updated_info: UserUpdate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Update logged-in user's profile information
    """
    user: UserSchema = get_user_from_jwt(request, db, response)

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if updated_info.display_name:
        cast(Any, user).display_name = updated_info.display_name
    if updated_info.email_address:
        cast(Any, user).email_address = updated_info.email_address

    db.commit()
    db.refresh(user)

    renew_user_token(str(user.id), response)

    return UserBase.model_validate(
        {
            "id": user.id,
            "email_address": user.email,
            "display_name": user.display_name,
            "user_type": user.user_type,
            "created": user.created_at or datetime.now(timezone.utc),
        }
    )

