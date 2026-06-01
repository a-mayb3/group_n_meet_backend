from sqlalchemy.dialects import postgresql
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from database import Base
import uuid


class EventSchema(Base):
    __tablename__ = "events"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4, server_default=text("gen_random_uuid()"))
    name = Column(String, index=True)
    description = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    place = Column(String, index=True)

    is_cancelled = Column(postgresql.BOOLEAN, default=False)

    organizer_group_id = Column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("organizer_groups.id"),
        index=True,
    )

    organizer_group = relationship(
        "OrganizerGroupSchema",
        back_populates="events",
        foreign_keys=[organizer_group_id],
    )
