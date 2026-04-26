import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

pytestmark = pytest.mark.asyncio


def build_payload(**overrides):
    payload = {
        "source_event_id": f"src-{uuid4()}",
        "event_type": "DEBRIS",
        "severity": "HIGH",
        "description": "Debris detected on the highway shoulder.",
        "confidence": 0.92,
        "camera_id": "CAM-001",
        "highway_id": "E1",
        "road_marker": "K12+300",
        "lane_no": "2",
        "latitude": 35.68,
        "longitude": 139.76,
        "image_url": "https://example.com/incidents/1.jpg",
        "detected_at": datetime.now(timezone.utc).isoformat(),
        "extra_payload": {"source": "test"},
    }
    payload.update(overrides)
    return payload


async def test_create_get_and_deduplicate_incident(client):
    payload = build_payload()

    create_response = await client.post("/events", json=payload)
    assert create_response.status_code == 201
    assert create_response.json()["meta"]["deduplicated"] is False

    created = create_response.json()["data"]
    assert created["detected_at"].endswith("Z")
    assert created["ingested_at"].endswith("Z")
    assert created["updated_at"].endswith("Z")
    get_response = await client.get(f"/events/{created['id']}")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["camera_id"] == "CAM-001"

    duplicate_response = await client.post("/events", json=payload)
    assert duplicate_response.status_code == 200
    assert duplicate_response.json()["meta"]["deduplicated"] is True
    assert duplicate_response.json()["data"]["id"] == created["id"]

    conflict_payload = build_payload(
        source_event_id=payload["source_event_id"],
        severity="CRITICAL",
        detected_at=payload["detected_at"],
    )
    conflict_response = await client.post("/events", json=conflict_payload)
    assert conflict_response.status_code == 409
    assert conflict_response.json()["error"]["code"] == "DUPLICATE_CONFLICT"


async def test_create_incident_without_coordinates(client):
    payload = build_payload(latitude=None, longitude=None)

    response = await client.post("/events", json=payload)

    assert response.status_code == 201
    assert response.json()["data"]["latitude"] is None
    assert response.json()["data"]["longitude"] is None
    assert response.json()["data"]["detected_at"].endswith("Z")


async def test_list_filter_and_sort(client):
    now = datetime.now(timezone.utc)
    payloads = [
        build_payload(severity="LOW", event_type="CONGESTION", detected_at=(now - timedelta(minutes=5)).isoformat()),
        build_payload(severity="CRITICAL", event_type="DEBRIS", detected_at=(now - timedelta(minutes=1)).isoformat()),
        build_payload(severity="HIGH", event_type="STOPPED_VEHICLE", detected_at=(now - timedelta(minutes=3)).isoformat()),
    ]

    responses = []
    for payload in payloads:
        response = await client.post("/events", json=payload)
        assert response.status_code == 201
        responses.append(response.json()["data"])

    ack_response = await client.patch(
        f"/events/{responses[2]['id']}/status",
        json={"status": "ACKNOWLEDGED", "status_note": "Operator reviewing"},
    )
    assert ack_response.status_code == 200

    list_response = await client.get(
        "/events",
        params={
            "severity": "HIGH,CRITICAL",
            "event_type": "DEBRIS,STOPPED_VEHICLE",
            "status": "NEW,ACKNOWLEDGED",
            "sort_by": "severity",
            "limit": 10,
            "offset": 0,
        },
    )
    body = list_response.json()

    assert list_response.status_code == 200
    assert body["meta"]["total"] == 2
    assert body["meta"]["limit"] == 10
    assert body["meta"]["offset"] == 0
    assert [item["severity"] for item in body["data"]] == ["CRITICAL", "HIGH"]


async def test_advanced_filters_and_summary_meta(client):
    now = datetime.now(timezone.utc)
    matching_source_id = f"advanced-old-{uuid4()}"
    payloads = [
        build_payload(
            source_event_id=matching_source_id,
            severity="CRITICAL",
            camera_id="CAM-ALPHA-001",
            highway_id="E1",
            road_marker="K90+100",
            lane_no="3",
            confidence=0.84,
            detected_at=(now - timedelta(seconds=140)).isoformat(),
        ),
        build_payload(
            source_event_id=f"advanced-new-{uuid4()}",
            severity="HIGH",
            camera_id="CAM-BETA-001",
            highway_id="E2",
            road_marker="K10+000",
            lane_no="1",
            confidence=0.97,
            detected_at=(now - timedelta(seconds=5)).isoformat(),
        ),
        build_payload(
            source_event_id=f"advanced-low-{uuid4()}",
            severity="LOW",
            camera_id="CAM-ALPHA-002",
            highway_id="E1",
            road_marker="K90+300",
            lane_no="2",
            confidence=0.52,
            detected_at=(now - timedelta(seconds=20)).isoformat(),
        ),
    ]

    for payload in payloads:
        response = await client.post("/events", json=payload)
        assert response.status_code == 201

    list_response = await client.get(
        "/events",
        params={
            "camera_query": "K90",
            "camera_id": "ALPHA",
            "source_event_id": matching_source_id[:18],
            "detected_from": (now - timedelta(minutes=5)).isoformat(),
            "detected_to": now.isoformat(),
            "min_delay_seconds": 60,
            "min_confidence": 0.8,
            "max_confidence": 0.9,
            "sort_by": "detection_delay",
            "order": "desc",
            "limit": 5,
            "offset": 0,
        },
    )
    body = list_response.json()

    assert list_response.status_code == 200
    assert body["meta"]["total"] == 1
    assert body["meta"]["critical_total"] == 1
    assert body["meta"]["avg_delay_seconds_total"] >= 60
    assert body["meta"]["latest_updated_at"].endswith("Z")
    assert body["data"][0]["source_event_id"] == matching_source_id


async def test_status_transition(client):
    create_response = await client.post("/events", json=build_payload())
    incident_id = create_response.json()["data"]["id"]

    noop_response = await client.patch(f"/events/{incident_id}/status", json={"status": "NEW"})
    assert noop_response.status_code == 200
    assert noop_response.json()["meta"]["noop"] is True

    ack_response = await client.patch(f"/events/{incident_id}/status", json={"status": "ACKNOWLEDGED"})
    assert ack_response.status_code == 200
    assert ack_response.json()["data"]["status"] == "ACKNOWLEDGED"

    resolved_response = await client.patch(f"/events/{incident_id}/status", json={"status": "RESOLVED"})
    assert resolved_response.status_code == 200
    assert resolved_response.json()["data"]["status"] == "RESOLVED"

    backtrack_response = await client.patch(f"/events/{incident_id}/status", json={"status": "ACKNOWLEDGED"})
    assert backtrack_response.status_code == 200
    assert backtrack_response.json()["data"]["status"] == "ACKNOWLEDGED"

    reset_response = await client.patch(f"/events/{incident_id}/status", json={"status": "NEW"})
    assert reset_response.status_code == 200
    assert reset_response.json()["data"]["status"] == "NEW"


async def test_validation_and_not_found(client):
    invalid_response = await client.post("/events", json=build_payload(confidence=1.4))
    assert invalid_response.status_code == 422
    assert invalid_response.json()["error"]["code"] == "VALIDATION_ERROR"

    missing_response = await client.get("/events/missing-id")
    assert missing_response.status_code == 404
    assert missing_response.json()["error"]["code"] == "NOT_FOUND"


async def test_api_broadcasts_sse_messages(client):
    sse_manager = client._transport.app.state.sse_manager
    queue = await sse_manager.connect()
    try:
        create_response = await client.post("/events", json=build_payload())
        incident = create_response.json()["data"]

        created_message = await queue.get()
        assert created_message["event"] == "incident.created"
        created_payload = json.loads(created_message["data"])
        assert created_payload["type"] == "INCIDENT_CREATED"
        assert created_payload["event_id"] == incident["id"]
        assert created_payload["payload"]["source_event_id"] == incident["source_event_id"]

        await client.patch(
            f"/events/{incident['id']}/status",
            json={"status": "ACKNOWLEDGED", "status_note": "Operator confirmed"},
        )

        updated_message = await queue.get()
        assert updated_message["event"] == "incident.status_updated"
        updated_payload = json.loads(updated_message["data"])
        assert updated_payload["type"] == "INCIDENT_STATUS_UPDATED"
        assert updated_payload["event_id"] == incident["id"]
        assert updated_payload["status"] == "ACKNOWLEDGED"
        assert updated_payload["status_note"] == "Operator confirmed"
    finally:
        await sse_manager.disconnect(queue)
