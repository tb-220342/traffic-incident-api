from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.incident import (
    IncidentCreate,
    IncidentEnvelope,
    IncidentListEnvelope,
    SortBy,
    SortOrder,
    StatusUpdateRequest,
)
from app.services import incident_service

router = APIRouter(prefix="/events", tags=["events"])


def get_sse_manager(request: Request):
    return request.app.state.sse_manager


@router.post(
    "",
    response_model=IncidentEnvelope,
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    payload: IncidentCreate,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    incident, deduplicated = await incident_service.create_incident(payload, db, get_sse_manager(request))
    if deduplicated:
        response.status_code = status.HTTP_200_OK
    return {"success": True, "data": incident, "meta": {"deduplicated": deduplicated}}


@router.get("", response_model=IncidentListEnvelope)
def list_events(
    severity: str | None = Query(default=None, description="Comma-separated severity values"),
    event_type: str | None = Query(default=None, description="Comma-separated event types"),
    status_value: str | None = Query(default=None, alias="status", description="Comma-separated statuses"),
    camera_query: str | None = Query(default=None, description="Search camera, highway, marker, or lane text"),
    camera_id: str | None = Query(default=None),
    source_event_id: str | None = Query(default=None),
    highway_id: str | None = Query(default=None),
    detected_from: datetime | None = Query(default=None),
    detected_to: datetime | None = Query(default=None),
    ingested_from: datetime | None = Query(default=None),
    ingested_to: datetime | None = Query(default=None),
    min_delay_seconds: float | None = Query(default=None, ge=0),
    max_delay_seconds: float | None = Query(default=None, ge=0),
    min_confidence: float | None = Query(default=None, ge=0, le=1),
    max_confidence: float | None = Query(default=None, ge=0, le=1),
    sort_by: SortBy = Query(default="detected_at"),
    order: SortOrder = Query(default="desc"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    incidents, summary = incident_service.list_incidents(
        db=db,
        severity=severity,
        event_type=event_type,
        status_value=status_value,
        camera_query=camera_query,
        camera_id=camera_id,
        source_event_id=source_event_id,
        highway_id=highway_id,
        detected_from=detected_from,
        detected_to=detected_to,
        ingested_from=ingested_from,
        ingested_to=ingested_to,
        min_delay_seconds=min_delay_seconds,
        max_delay_seconds=max_delay_seconds,
        min_confidence=min_confidence,
        max_confidence=max_confidence,
        sort_by=sort_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return {
        "success": True,
        "data": incidents,
        "meta": {
            "total": summary["total"],
            "limit": limit,
            "offset": offset,
            "critical_total": summary["critical_total"],
            "avg_delay_seconds_total": summary["avg_delay_seconds_total"],
            "latest_updated_at": summary["latest_updated_at"],
        },
    }


@router.get("/{incident_id}", response_model=IncidentEnvelope)
def get_event(incident_id: str, db: Session = Depends(get_db)):
    incident = incident_service.get_incident_or_404(db, incident_id)
    return {"success": True, "data": incident, "meta": {}}


@router.patch("/{incident_id}/status", response_model=IncidentEnvelope)
async def patch_event_status(
    incident_id: str,
    payload: StatusUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    incident, noop = await incident_service.update_incident_status(
        db=db,
        incident_id=incident_id,
        new_status=payload.status,
        status_note=payload.status_note,
        sse_manager=get_sse_manager(request),
    )
    return {"success": True, "data": incident, "meta": {"noop": noop}}
