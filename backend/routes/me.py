from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db

from pyargon2 import hash

from schemas.user import User

class UserAuth(BaseModel):
    email_address: str
    password: str

router = APIRouter(
    prefix="/me",
    tags=["me"],
)

"""Get logged-in user information"""
@router.get("/")
def read_me(db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Not implemented yet")

"""Get logged-in user's organizer groups"""
@router.get("/organizer-groups")
def read_my_organizer_groups(db: Session = Depends(get_db)):
    raise HTTPException(status_code=501, detail="Not implemented yet")

@router.get("/login",status_code=401)
def login_user(auth: UserAuth, db: Session = Depends(get_db)):

    query =  db.query(User).filter(User.email == auth.email_address)
    user = query.first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    correctCredentials = hash(
        password=user.password_hash.encode(),
        salt=user.password_salt.encode(),
        variant="id"
        )
    
    givenCredentials = hash(
        password=auth.password,
        salt=user.password_salt.encode(),
        variant="id"
        )

    if (givenCredentials != correctCredentials):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
            )
    
    return {"message": "Login successful", "user_id": str(user.id)}


