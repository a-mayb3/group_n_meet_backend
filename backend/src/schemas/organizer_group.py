from sqlalchemy.dialects import postgresql
from sqlalchemy import Table, Column, Enum, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class GroupMemberRole(str, Enum):
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"

organizer_group_members = Table(
    "organizer_group_members",
    Base.metadata,
    Column("organizer_group_id", postgresql.UUID(as_uuid=True), ForeignKey("organizer_groups.id"), primary_key=True),
    Column("user_id", postgresql.UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True),

    ## fix: make GroupMemberRole wark with sqlalchemy and postgres
    Column("role", String, default=GroupMemberRole.MEMBER, nullable=False)
)

class OrganizerGroupSchema(Base):
    __tablename__ = "organizer_groups"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, index=True)

    created_at = Column(postgresql.TIMESTAMP, index=True)

    events = relationship("EventSchema", back_populates="organizer_group")

