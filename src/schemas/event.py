from sqlalchemy.dialects import postgresql
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base


class EventSchema(Base):
    __tablename__ = "events"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime, index=True)
    place = Column(String, index=True)

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
