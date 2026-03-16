from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db

from pyargon2 import hash

from schemas.user import UserSchema
from models.users import UserBase, UserAuth

router = APIRouter(
    prefix="/me",
    tags=["me"]
)

@router.get("/")
def get_personal_info(db: Session = Depends(get_db)):
    """
    Get logged-in user's profile information
    """
    raise NotImplementedError("Get personal info functionality is not implemented yet")
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.get("/organizer-groups")
def get_personal_organizer_groups(db: Session = Depends(get_db)):
    """
    Get logged-in user's organizer groups
    """
    raise NotImplementedError("Get personal organizer groups functionality is not implemented yet") 
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.post("/login", status_code=401)
def login_user(auth: UserAuth, db: Session = Depends(get_db)):

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
        password=auth.password,
        salt=user.password_salt.encode(),
        variant="id"
        )

    if (given_credentials != correct_credentials):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
            )
    
    return {"message": "Login successful", "user_id": str(user.id)}

@router.get("/reservations")
def get_personal_rsvps(db: Session = Depends(get_db)):
    """
    Get the current user's RSVPs.
    """
    raise NotImplementedError("Get personal RSVPs functionality is not implemented yet")
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.delete("/logout")
def logout_user():
    """
    Logout the current user.
    """
    raise NotImplementedError("Logout functionality is not implemented yet")
    raise HTTPException(status_code=501, detail="Not implemented yet")


## TODOS

## TODO: Implement GET get_personal_info()
## TODO: Implement GET get_personal_organizer_groups()
## TODO: Implement GET get_personal_rsvps()
## TODO: Implement DELETE logout_user()
## TODO: Move POST login_user() to a separate auth module
