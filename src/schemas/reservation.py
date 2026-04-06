from sqlalchemy.dialects import postgresql
from sqlalchemy import Table, Column, Boolean, ForeignKey, func
from database import Base

reservation = Table(
    "reservations",
    Base.metadata,

    Column("id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            index=True),

    Column("user_id",
            postgresql.UUID(as_uuid=True),
            ForeignKey("users.id"),
            nullable=False),

    Column("event_id",
            postgresql.UUID(as_uuid=True), 
            ForeignKey("events.id"),
            nullable=False),

    Column("reserved_at", 
            postgresql.TIMESTAMP,
            nullable=False,
            server_default=func.now()),

    Column("latest_change_at",
            postgresql.TIMESTAMP,
            nullable=False,
            server_default=func.now(),
            onupdate=func.now()),

    Column("is_cancelled",
            Boolean,
            default=False, 
            nullable=False),
)