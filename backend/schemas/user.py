from sqlalchemy.dialects import postgresql
from sqlalchemy import Column, Enum, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class UserType(str, Enum):
    REGULAR = "regular"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True)
    user_type = Column(Enum(UserType.REGULAR, UserType.ADMIN), default=UserType.REGULAR, nullable=False)

    display_name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    
    password_hash = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)

    created_at = Column(DateTime, index=True)

