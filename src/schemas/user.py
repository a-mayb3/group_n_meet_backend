import uuid
from sqlalchemy import Column, Enum, String, ForeignKey, text
from sqlalchemy.orm import relationship

from sqlalchemy.dialects.postgresql import UUID, ENUM, TIMESTAMP

from database import Base


class UserType(str, Enum):
    REGULAR = "regular"
    ADMIN = "admin"


class UserSchema(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        index=True,
        unique=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )

    ## fix: make UserType wark with sqlalchemy and postgres
    # user_type = Column(ENUM(UserType), default=UserType.REGULAR, nullable=False)
    user_type = Column(String, default=UserType.REGULAR, nullable=False)

    display_name = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)

    password_hash = Column(String, nullable=False)
    password_salt = Column(String, nullable=False)

    created_at = Column(
        TIMESTAMP, index=True, server_default=text("now()"), nullable=False
    )

    organizer_groups = relationship(
        "OrganizerGroupSchema",
        secondary="organizer_group_members",
        back_populates="members"
    )
