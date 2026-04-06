from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from database import get_db

from pyargon2 import hash

from schemas.user import UserSchema
from schemas.organizer_group import OrganizerGroupSchema, organizer_group_members
from schemas.reservation import reservation

from models.users import UserBase, UserAuth
from models.organizer_groups import OrganizerGroupBase
from models.rsvps import RSVPBase

from utils import get_user_from_jwt, renew_user_token

router = APIRouter(
    prefix="/me",
    tags=["me"]
)

@router.get("/", response_model=UserBase)
def get_personal_info(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Get logged-in user's profile information
    """
    user = get_user_from_jwt(request, db, response)
    return user

@router.get("/organizer-groups", response_model=list[OrganizerGroupBase])
def get_personal_organizer_groups(request: Request, response: Response, db: Session = Depends(get_db)):
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
        group
        for group in groups
    ]

@router.post("/login")
def login_user(auth: UserAuth, request: Request, response: Response, db: Session = Depends(get_db)):

    query =  db.query(UserSchema).filter(UserSchema.email == auth.email_address)
    user = query.first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    correct_credentials = hash(
        password=user.password_hash.encode(),
        salt=user.password_salt.encode(),
        variant="id"
        )
    
    given_credentials = hash(
        password=auth.password.get_secret_value(),
        salt=user.password_salt.encode(),
        variant="id"
        )

    if (given_credentials != correct_credentials):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
            )

    # set server-side session and cookie-based JWT
    try:
        request.session["user_id"] = str(user.id)
    except Exception:
        pass
    renew_user_token(str(user.id), response)
    
    return {"message": "Login successful", "user_id": str(user.id)}

@router.get("/reservations", response_model=list[RSVPBase])
def get_personal_rsvps(request: Request, response: Response, db: Session = Depends(get_db)):
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
        {
            "user_id": row.user_id,
            "event_id": row.event_id,
            "reserved_at": row.reserved_at,
            "is_cancelled": row.is_cancelled,
        }
        for row in rows
    ]

@router.delete("/logout")
def logout_user(request: Request, response: Response):
    """
    Logout the current user.
    """
    try:
        request.session.clear()
    except Exception:
        pass
    response.delete_cookie("access_token")
    return {"message": "Logout successful"}


## TODOS

## TODO: Implement GET get_personal_info()
## TODO: Implement GET get_personal_organizer_groups()
## TODO: Implement GET get_personal_rsvps()
## TODO: Implement DELETE logout_user()
## TODO: Move POST login_user() to a separate auth module
