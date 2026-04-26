from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.core.enums import EventType, Severity, Status


def to_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class IncidentCreate(BaseModel):
    source_event_id: str = Field(min_length=1, max_length=128)
    event_type: EventType
    severity: Severity
    description: str | None = Field(default=None, max_length=5000)
    confidence: float = Field(ge=0.0, le=1.0)
    camera_id: str = Field(min_length=1, max_length=64)
    highway_id: str | None = Field(default=None, max_length=32)
    road_marker: str | None = Field(default=None, max_length=64)
    lane_no: str | None = Field(default=None, max_length=16)
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)
    image_url: str | None = Field(default=None, max_length=500)
    detected_at: datetime
    extra_payload: dict[str, Any] | None = None

    model_config = ConfigDict(from_attributes=True)

    @field_validator("detected_at", mode="after")
    @classmethod
    def normalize_detected_at(cls, value: datetime) -> datetime:
        return to_utc(value)


class IncidentResponse(IncidentCreate):
    id: str
    status: Status
    status_note: str | None = None
    ingested_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("ingested_at", "updated_at", mode="after")
    @classmethod
    def normalize_response_datetimes(cls, value: datetime) -> datetime:
        return to_utc(value)

    @field_serializer("detected_at", "ingested_at", "updated_at", when_used="json")
    def serialize_datetimes(self, value: datetime) -> str:
        return to_utc(value).isoformat().replace("+00:00", "Z")


class StatusUpdateRequest(BaseModel):
    status: Status
    status_note: str | None = Field(default=None, max_length=5000)


class ResponseMeta(BaseModel):
    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    critical_total: int | None = None
    avg_delay_seconds_total: int | None = None
    latest_updated_at: datetime | None = None
    deduplicated: bool | None = None
    noop: bool | None = None

    @field_serializer("latest_updated_at", when_used="json")
    def serialize_latest_updated_at(self, value: datetime | None) -> str | None:
        if value is None:
            return None
        return to_utc(value).isoformat().replace("+00:00", "Z")


class ErrorResponse(BaseModel):
    code: str
    message: str
    details: list[dict] | dict | None = None


class IncidentEnvelope(BaseModel):
    success: bool = True
    data: IncidentResponse
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class IncidentListEnvelope(BaseModel):
    success: bool = True
    data: list[IncidentResponse]
    meta: ResponseMeta = Field(default_factory=ResponseMeta)


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorResponse


SortBy = Literal["detected_at", "ingested_at", "updated_at", "severity", "confidence", "detection_delay"]
SortOrder = Literal["asc", "desc"]
