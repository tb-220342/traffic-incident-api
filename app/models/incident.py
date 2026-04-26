from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Enum as SqlEnum, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import EventType, Severity, Status
from app.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class IncidentEvent(Base):
    __tablename__ = "incident_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_event_id: Mapped[str] = mapped_column(String(128), nullable=False, unique=True, index=True)
    event_type: Mapped[EventType] = mapped_column(SqlEnum(EventType, name="event_type"), nullable=False)
    severity: Mapped[Severity] = mapped_column(SqlEnum(Severity, name="severity"), nullable=False)
    status: Mapped[Status] = mapped_column(
        SqlEnum(Status, name="status"),
        nullable=False,
        default=Status.NEW,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    camera_id: Mapped[str] = mapped_column(String(64), nullable=False)
    highway_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    road_marker: Mapped[str | None] = mapped_column(String(64), nullable=True)
    lane_no: Mapped[str | None] = mapped_column(String(16), nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ingested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    status_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=utcnow,
        onupdate=utcnow,
    )
