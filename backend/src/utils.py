import os

from fastapi import APIRouter, Depends, HTTPException, Request, status, Response
from backend.src.database import db_dependency
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import models

import schemas.user as user_schemas

from pyargon2 import hash

from backend.src.config import SESSION_SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict, expires_delta: timedelta | None = None): 
    """Create a JWT token"""

    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    to_encode.update({"iat": datetime.now(timezone.utc)})
    encoded_jwt = jwt.encode(to_encode, SESSION_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_jwt_token(token: str):
    """Verify and decode a JWT token"""
    
    try:
        payload = jwt.decode(token, SESSION_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return user_id
    
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
def get_user_from_jwt(request: Request, db: db_dependency) -> user_schemas.UserSchema:
    """Helper function to check for valid JWT token in cookies"""

    get_token = request.cookies.get("access_token")
    
    if not get_token or get_token is None:
        raise HTTPException(
            status_code=401,
            detail="Not logged in"
        )
    try:
        user_id: str = verify_jwt_token(get_token)  ## verifying token validity

        db_user = db.query(user_schemas.UserSchema.UserBase).filter(user_schemas.UserSchema.id == int(user_id)).first()
        if db_user is None:
            request.cookies.clear() ## removing invalid auth cookie
            raise HTTPException(
                status_code=401,
                detail="Could not verify credentials"
            )
        return db_user
    except HTTPException:
        request.cookies.clear() ## removing invalid auth cookie
        raise

def verify_user_password(user_id: int, password: str, db: db_dependency) -> None:
    """Verify user's password"""
    db_user = db.query(user_schemas.UserSchema.UserBase).filter(user_schemas.UserSchema.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Could not verify credentials")
    
    hashed_password = hash(password=password, salt=str(getattr(db_user,"password_salt")), variant="id")
    if hashed_password != db_user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Could not verify credentials")
    
def renew_user_token(user_id: int, response: Response):
    """Renew user's JWT token by creating a new one and setting it in the cookies"""
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True)