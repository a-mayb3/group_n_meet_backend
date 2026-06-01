import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import EmailStr
from sqlalchemy.orm import Session

from database import get_db
from models.users import UserBase
from schemas.user import UserSchema

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/search", response_model=list[UserBase])
def search_users(
    q: str = Query("", description="Search query for email address or display name"),
    db: Session = Depends(get_db)
):
    """
    Search for users by email address or display name.
    """
    query = db.query(UserSchema)

    if q:
        query = query.filter(
            (UserSchema.email.ilike(f"%{q}%")) | (UserSchema.display_name.ilike(f"%{q}%"))
        )

    users = query.all()

    return [
        UserBase.model_validate(
            {
                "id": user.id,
                "email_address": user.email,
                "display_name": user.display_name,
                "user_type": user.user_type,
                "created": user.created_at or datetime.now(timezone.utc),
            }
        )
        for user in users
    ]

@router.get("/{user_id}", response_model=UserBase)
def get_user_by_id(user_id: str, db: Session = Depends(get_db)):
    """
    Get user information by user ID.
    """
    user = db.query(UserSchema).filter(UserSchema.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserBase.model_validate(
        {
            "id": user.id,
            "email_address": user.email,
            "display_name": user.display_name,
            "user_type": user.user_type,
            "created": user.created_at or datetime.now(timezone.utc),
        }
    )