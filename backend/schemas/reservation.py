from sqlalchemy.dialects import postgresql
from sqlalchemy import Boolean, Column, ForeignKey, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Table

reservation = Table(
    "reservation",
    Base.metadata,
    Column("user_id", postgresql.UUID(as_uuid=True), ForeignKey("users.id"), nullable=False),
    Column("event_id", postgresql.UUID(as_uuid=True), ForeignKey("events.id"), nullable=False),
    Column("reserved_at", DateTime, index=True, nullable=False),
    Column("is_cancelled", Boolean, default=False, nullable=False),

    Column("hash_code", postgresql.BYTEA, primary_key=True, unique=True, index=True, nullable=False), 
    # hash from user_id + event_id + reserved_at + is_cancelled for integrity verification
)