import logging
import os

from database import get_db
from utils import renew_user_token

from schemas.user import UserSchema
from models.users import UserBase, UserAuth, UserCreate

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from pyargon2 import hash

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

logger = logging.getLogger(__name__)

@router.post("/login")
def login_user(auth: UserAuth, request: Request, response: Response, db: Session = Depends(get_db)):

    query =  db.query(UserSchema).filter(UserSchema.email == auth.email_address)
    user: UserSchema = query.first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    correct_credentials = hash(
        password=user.password_hash.encode(),
        salt=user.password_salt.encode(),
        variant="id",
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

@router.post("/register", response_model=UserBase)
def register_user(auth: UserCreate, request: Request, response: Response, db: Session = Depends(get_db)):

    existing_user = db.query(UserSchema).filter(UserSchema.email == auth.email_address).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    salt = os.urandom(32).hex()

    password_hash = hash(
        password=auth.password.get_secret_value(),
        salt=salt,
        variant="id"
    )

    new_user = UserSchema(
        email=auth.email_address,
        display_name=auth.display_name,
        password_hash=password_hash,
        password_salt=salt
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # set server-side session and cookie-based JWT
    try:
        request.session["user_id"] = str(new_user.id)
    except Exception:
        pass
    renew_user_token(str(new_user.id), response)

    return UserBase.model_validate(new_user)