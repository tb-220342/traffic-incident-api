from datetime import datetime, timezone
from enum import Enum

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.core.enums import EventType, Severity, Status
from app.repositories import incident_repository
from app.schemas.incident import IncidentCreate, IncidentResponse, SortBy, SortOrder
from app.services.sse_manager import SSEManager

ALLOWED_STATUS_TRANSITIONS = {
    Status.NEW: {Status.ACKNOWLEDGED, Status.RESOLVED},
    Status.ACKNOWLEDGED: {Status.NEW, Status.DISPATCHED, Status.RESOLVED},
    Status.DISPATCHED: {Status.ACKNOWLEDGED, Status.RESOLVED},
    Status.RESOLVED: {Status.ACKNOWLEDGED, Status.DISPATCHED},
}


def normalize_incident_payload(payload: dict) -> dict:
    normalized = dict(payload)
    detected_at = normalized.get("detected_at")
    if isinstance(detected_at, datetime) and detected_at.tzinfo is None:
        normalized["detected_at"] = detected_at.replace(tzinfo=timezone.utc)
    return normalized


def normalize_datetime_filter(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def build_error_detail(code: str, message: str, details: list[dict] | dict | None = None) -> dict:
    return {
        "code": code,
        "message": message,
        "details": details,
    }


def get_logger(sse_manager: SSEManager):
    return getattr(sse_manager, "_logger", None)


def parse_enum_filter_list(
    raw_value: str | None,
    enum_type: type[Enum],
    field_name: str,
) -> list[Enum] | None:
    if not raw_value:
        return None

    values = [value.strip().upper() for value in raw_value.split(",") if value.strip()]
    if not values:
        return None

    try:
        return [enum_type(value) for value in values]
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=build_error_detail(
                code="VALIDATION_ERROR",
                message=f"Invalid {field_name} filter: {raw_value}",
            ),
        ) from exc


async def create_incident(
    payload: IncidentCreate,
    db: Session,
    sse_manager: SSEManager,
) -> tuple[IncidentResponse, bool]:
    logger = get_logger(sse_manager)
    existing = incident_repository.get_incident_by_source_event_id(db, payload.source_event_id)
    if existing is not None:
        existing_payload = normalize_incident_payload(IncidentCreate.model_validate(existing).model_dump(mode="python"))
        incoming_payload = normalize_incident_payload(payload.model_dump(mode="python"))
        if existing_payload != incoming_payload:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=build_error_detail(
                    code="DUPLICATE_CONFLICT",
                    message="An incident with the same source_event_id already exists but has different content",
                ),
            )
        if logger:
            logger.info("incident_deduplicated source_event_id=%s", payload.source_event_id)
        return IncidentResponse.model_validate(existing), True

    incident = incident_repository.create_incident(db, payload)
    response = IncidentResponse.model_validate(incident)
    if logger:
        logger.info(
            "incident_created id=%s source_event_id=%s event_type=%s severity=%s",
            response.id,
            response.source_event_id,
            response.event_type.value,
            response.severity.value,
        )
    await sse_manager.broadcast(
        event_name="incident.created",
        data=jsonable_encoder(
            {
                "type": "INCIDENT_CREATED",
                "event_id": response.id,
                "payload": response,
            }
        ),
    )
    return response, False


def list_incidents(
    db: Session,
    severity: str | None,
    event_type: str | None,
    status_value: str | None,
    camera_query: str | None,
    camera_id: str | None,
    source_event_id: str | None,
    highway_id: str | None,
    detected_from: datetime | None,
    detected_to: datetime | None,
    ingested_from: datetime | None,
    ingested_to: datetime | None,
    min_delay_seconds: float | None,
    max_delay_seconds: float | None,
    min_confidence: float | None,
    max_confidence: float | None,
    sort_by: SortBy,
    order: SortOrder,
    limit: int,
    offset: int,
) -> tuple[list[IncidentResponse], dict]:
    severities = parse_enum_filter_list(severity, Severity, "severity")
    event_types = parse_enum_filter_list(event_type, EventType, "event_type")
    statuses = parse_enum_filter_list(status_value, Status, "status")
    incidents, summary = incident_repository.list_incidents(
        db=db,
        severities=severities,
        event_types=event_types,
        statuses=statuses,
        camera_query=camera_query,
        camera_id=camera_id,
        source_event_id=source_event_id,
        highway_id=highway_id,
        detected_from=normalize_datetime_filter(detected_from),
        detected_to=normalize_datetime_filter(detected_to),
        ingested_from=normalize_datetime_filter(ingested_from),
        ingested_to=normalize_datetime_filter(ingested_to),
        min_delay_seconds=min_delay_seconds,
        max_delay_seconds=max_delay_seconds,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return [IncidentResponse.model_validate(item) for item in incidents], summary


def get_incident_or_404(db: Session, incident_id: str) -> IncidentResponse:
    incident = incident_repository.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=build_error_detail(code="NOT_FOUND", message="Incident not found"),
        )
    return IncidentResponse.model_validate(incident)


async def update_incident_status(
    db: Session,
    incident_id: str,
    new_status: Status,
    status_note: str | None,
    sse_manager: SSEManager,
) -> tuple[IncidentResponse, bool]:
    logger = get_logger(sse_manager)
    incident = incident_repository.get_incident(db, incident_id)
    if incident is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=build_error_detail(code="NOT_FOUND", message="Incident not found"),
        )

    if incident.status == new_status:
        if logger:
            logger.info("incident_status_noop id=%s status=%s", incident_id, new_status.value)
        return IncidentResponse.model_validate(incident), True

    allowed = ALLOWED_STATUS_TRANSITIONS[incident.status]
    if new_status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=build_error_detail(
                code="INVALID_STATUS_TRANSITION",
                message=f"Cannot transition from {incident.status.value} to {new_status.value}",
            ),
        )

    previous_status = incident.status
    updated = incident_repository.update_incident_status(db, incident, new_status, status_note=status_note)
    response = IncidentResponse.model_validate(updated)
    if logger:
        logger.info(
            "incident_status_updated id=%s previous_status=%s status=%s",
            response.id,
            previous_status.value,
            response.status.value,
        )
    await sse_manager.broadcast(
        event_name="incident.status_updated",
        data=jsonable_encoder(
            {
                "type": "INCIDENT_STATUS_UPDATED",
                "event_id": response.id,
                "previous_status": previous_status,
                "status": response.status,
                "updated_at": response.updated_at,
                "status_note": response.status_note,
            }
        ),
    )
    return response, False
