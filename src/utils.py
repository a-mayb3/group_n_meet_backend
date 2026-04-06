from uuid import UUID
from datetime import datetime, timedelta, timezone

from pydantic import SecretStr
from fastapi import HTTPException, Request, status, Response
from jose import JWTError, jwt
from pyargon2 import hash
from sqlalchemy.orm import Session

from schemas.user import UserSchema

from config import Settings

settings = Settings()

def create_access_token(data: dict, expires_delta: timedelta | None = None): 
    """Create a JWT token"""

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    to_encode.update({"iat": datetime.now(timezone.utc)})

    encoded_jwt = jwt.encode(to_encode, settings.SESSION_SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt

def verify_jwt_token(token: str):
    """
    Verify and decode a JWT token
    """
    
    try:
        payload = jwt.decode(token=token, key=settings.SESSION_SECRET_KEY, algorithms=[settings.ALGORITHM])
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
    
def get_user_from_jwt(request: Request, db: Session, response: Response | None = None) -> UserSchema:
    """Helper function to check for valid JWT token in cookies.

    If a token is missing or invalid, this will clear the auth cookie
    (and server-side session if present) when a `response` is provided.
    """

    def _invalidate():
        try:
            if response is not None:
                response.delete_cookie("access_token")
        finally:
            # clear any server session state if SessionMiddleware is active
            try:
                request.session.clear()
            except Exception:
                pass

    get_token = request.cookies.get("access_token")

    if not get_token:
        _invalidate()
        raise HTTPException(
            status_code=401,
            detail="Not logged in",
        )

    try:
        user_id: str = verify_jwt_token(get_token)  ## verifying token validity
        db_user = db.query(UserSchema).filter(UserSchema.id == UUID(user_id)).first()
        if db_user is None:
            _invalidate()
            raise HTTPException(
                status_code=401,
                detail="Could not verify credentials",
            )
        return db_user
    except HTTPException:
        _invalidate()
        raise

def verify_user_password(user_id: UUID, password: SecretStr, db: Session) -> None:
    """Verify user's password"""
    db_user = db.query(UserSchema).filter(UserSchema.id == user_id).first()
    if db_user is None:
        raise HTTPException(
            status_code=401,
            detail="Could not verify credentials")
    
    hashed_password = hash(
        password=password.get_secret_value(),
        salt=str(getattr(db_user, "password_salt")),
        variant="id",
    )
    if hashed_password != db_user.password_hash:
        raise HTTPException(
            status_code=401,
            detail="Could not verify credentials")
    
def renew_user_token(user_id: UUID | str, response: Response):
    """Renew user's JWT token by creating a new one and setting it in the cookies"""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user_id)}, expires_delta=access_token_expires
    )
    response.set_cookie(key="access_token", value=access_token, httponly=True, samesite="lax")