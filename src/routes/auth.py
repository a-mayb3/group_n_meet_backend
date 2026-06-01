import logging
import os
from datetime import datetime, timezone

from database import get_db
from utils import renew_user_token

from schemas.user import UserSchema
from models.users import UserBase, UserAuth, UserCreate

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pyargon2 import hash

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

logger = logging.getLogger(__name__)


@router.post("/login")
def login_user(
    auth: UserAuth, request: Request, response: Response, db: Session = Depends(get_db)
):

    query = db.query(UserSchema).filter(UserSchema.email == auth.email_address)
    user: UserSchema = query.first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Hash the provided password with the stored salt and compare to stored hash
    given_credentials = hash(
        password=auth.password.get_secret_value(),
        salt=str(user.password_salt),
        variant="id",
    )

    if given_credentials != user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

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
def register_user(
    auth: UserCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):

    # check for existing email or display name to avoid DB unique constraint errors
    existing_user = (
        db.query(UserSchema).filter(UserSchema.email == auth.email_address).first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    existing_display = (
        db.query(UserSchema)
        .filter(UserSchema.display_name == auth.display_name)
        .first()
    )
    if existing_display:
        raise HTTPException(status_code=400, detail="Display name already taken")

    salt = os.urandom(32).hex()

    password_hash = hash(
        password=auth.password.get_secret_value(), salt=salt, variant="id"
    )

    new_user = UserSchema(
        email=auth.email_address,
        display_name=auth.display_name,
        password_hash=password_hash,
        password_salt=salt,
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Email or display name already registered"
        )

    return UserBase.model_validate(
        {
            "id": new_user.id,
            "email_address": new_user.email,
            "display_name": new_user.display_name,
            "user_type": new_user.user_type,
            "created": new_user.created_at or datetime.now(timezone.utc),
        }
    )
