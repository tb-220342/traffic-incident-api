from datetime import datetime

from sqlalchemy import asc, case, desc, func, or_, select
from sqlalchemy.orm import Session

from app.core.enums import EventType, Severity, Status
from app.models.incident import IncidentEvent
from app.schemas.incident import IncidentCreate, SortBy, SortOrder

SEVERITY_SORT_ORDER = case(
    (IncidentEvent.severity == Severity.CRITICAL, 4),
    (IncidentEvent.severity == Severity.HIGH, 3),
    (IncidentEvent.severity == Severity.MEDIUM, 2),
    (IncidentEvent.severity == Severity.LOW, 1),
    else_=0,
)

DETECTION_DELAY_SECONDS = (
    func.julianday(IncidentEvent.ingested_at) - func.julianday(IncidentEvent.detected_at)
) * 86400.0


def contains_text(column, value: str):
    return column.ilike(f"%{value.strip()}%")


def apply_filters(
    stmt,
    severities: list[Severity] | None,
    event_types: list[EventType] | None,
    statuses: list[Status] | None,
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
):
    if severities:
        stmt = stmt.where(IncidentEvent.severity.in_(severities))

    if event_types:
        stmt = stmt.where(IncidentEvent.event_type.in_(event_types))

    if statuses:
        stmt = stmt.where(IncidentEvent.status.in_(statuses))

    if camera_query:
        stmt = stmt.where(
            or_(
                contains_text(IncidentEvent.camera_id, camera_query),
                contains_text(IncidentEvent.highway_id, camera_query),
                contains_text(IncidentEvent.road_marker, camera_query),
                contains_text(IncidentEvent.lane_no, camera_query),
            )
        )

    if camera_id:
        stmt = stmt.where(contains_text(IncidentEvent.camera_id, camera_id))

    if source_event_id:
        stmt = stmt.where(contains_text(IncidentEvent.source_event_id, source_event_id))

    if highway_id:
        stmt = stmt.where(contains_text(IncidentEvent.highway_id, highway_id))

    if detected_from:
        stmt = stmt.where(IncidentEvent.detected_at >= detected_from)

    if detected_to:
        stmt = stmt.where(IncidentEvent.detected_at <= detected_to)

    if ingested_from:
        stmt = stmt.where(IncidentEvent.ingested_at >= ingested_from)

    if ingested_to:
        stmt = stmt.where(IncidentEvent.ingested_at <= ingested_to)

    if min_delay_seconds is not None:
        stmt = stmt.where(DETECTION_DELAY_SECONDS >= min_delay_seconds)

    if max_delay_seconds is not None:
        stmt = stmt.where(DETECTION_DELAY_SECONDS <= max_delay_seconds)

    if min_confidence is not None:
        stmt = stmt.where(IncidentEvent.confidence >= min_confidence)

    if max_confidence is not None:
        stmt = stmt.where(IncidentEvent.confidence <= max_confidence)

    return stmt


def create_incident(db: Session, payload: IncidentCreate) -> IncidentEvent:
    incident = IncidentEvent(**payload.model_dump())
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident


def get_incident(db: Session, incident_id: str) -> IncidentEvent | None:
    stmt = select(IncidentEvent).where(IncidentEvent.id == incident_id)
    return db.execute(stmt).scalar_one_or_none()


def get_incident_by_source_event_id(db: Session, source_event_id: str) -> IncidentEvent | None:
    stmt = select(IncidentEvent).where(IncidentEvent.source_event_id == source_event_id)
    return db.execute(stmt).scalar_one_or_none()


def list_incidents(
    db: Session,
    severities: list[Severity] | None,
    event_types: list[EventType] | None,
    statuses: list[Status] | None,
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
) -> tuple[list[IncidentEvent], dict]:
    stmt = select(IncidentEvent)
    summary_stmt = select(
        func.count().label("total"),
        func.coalesce(
            func.sum(case((IncidentEvent.severity == Severity.CRITICAL, 1), else_=0)),
            0,
        ).label("critical_total"),
        func.avg(DETECTION_DELAY_SECONDS).label("avg_delay_seconds_total"),
        func.max(IncidentEvent.updated_at).label("latest_updated_at"),
    ).select_from(IncidentEvent)

    filter_args = {
        "severities": severities,
        "event_types": event_types,
        "statuses": statuses,
        "camera_query": camera_query,
        "camera_id": camera_id,
        "source_event_id": source_event_id,
        "highway_id": highway_id,
        "detected_from": detected_from,
        "detected_to": detected_to,
        "ingested_from": ingested_from,
        "ingested_to": ingested_to,
        "min_delay_seconds": min_delay_seconds,
        "max_delay_seconds": max_delay_seconds,
        "min_confidence": min_confidence,
        "max_confidence": max_confidence,
    }
    stmt = apply_filters(stmt, **filter_args)
    summary_stmt = apply_filters(summary_stmt, **filter_args)

    sort_column = {
        "detected_at": IncidentEvent.detected_at,
        "ingested_at": IncidentEvent.ingested_at,
        "updated_at": IncidentEvent.updated_at,
        "severity": SEVERITY_SORT_ORDER,
        "confidence": IncidentEvent.confidence,
        "detection_delay": DETECTION_DELAY_SECONDS,
    }[sort_by]
    stmt = stmt.order_by(asc(sort_column) if order == "asc" else desc(sort_column))
    stmt = stmt.offset(offset).limit(limit)

    incidents = db.execute(stmt).scalars().all()
    summary_row = db.execute(summary_stmt).one()
    summary = {
        "total": summary_row.total,
        "critical_total": summary_row.critical_total,
        "avg_delay_seconds_total": (
            round(summary_row.avg_delay_seconds_total)
            if summary_row.avg_delay_seconds_total is not None
            else None
        ),
        "latest_updated_at": summary_row.latest_updated_at,
    }
    return incidents, summary


def update_incident_status(
    db: Session,
    incident: IncidentEvent,
    status: Status,
    status_note: str | None = None,
) -> IncidentEvent:
    incident.status = status
    incident.status_note = status_note
    db.add(incident)
    db.commit()
    db.refresh(incident)
    return incident
