# Requirements Specification - Traffic Incident Monitoring API Platform

Languages: [English](requirements-spec.en.md) | [日本語](requirements-spec.ja.md) | [繁體中文](requirements-spec.zh-Hant.md)

[Back to Documentation Index](document-index.md) | [Project README](../README.md)

> [!NOTE]
> This is the normalized requirements reference used to validate the implementation against the assignment scope and the extended project plan.

Source PDF: [requirements_spec.md.pdf](requirements_spec.md.pdf)

This is an English translation of the requirements definition document prepared for the Back-End Candidate Evaluation.

## 01 Project Overview

| Item | Content |
| --- | --- |
| System name | Traffic Incident Monitoring API Platform |
| Purpose | Receive incident events detected by an AI video-analysis system and deliver them to the dispatch center in near real time. |
| Target users | Highway operation center staff. |
| Submission format | Git repository, README, and AI conversation log. |
| Technical constraints | None. Language, framework, and dependencies are free to choose. |

Design principle: **Speed matters.** The system minimizes latency from detection to display by using SSE-based real-time push.

## 02 Functional Requirements

### Required

| ID | Endpoint | Content |
| --- | --- | --- |
| F-01 | `POST /events` | Receive events from the AI detection system. Validate the request with Pydantic and immediately broadcast the accepted event through SSE. |
| F-02 | `GET /events` | Return an event list. Support filtering by `severity`, `event_type`, and `status`; sorting by `detected_at` or `severity`; and pagination. |
| F-03 | `GET /events/{id}` | Return one event. Return `404` when the event does not exist. |

### Nice To Have

| ID | Feature | Content |
| --- | --- | --- |
| F-04 | `GET /events/stream` | Long-lived SSE connection. Every new `POST /events` should be pushed immediately to all dashboard clients. This directly answers "Speed matters." |
| F-05 | `PATCH /events/{id}/status` | Update status through `NEW -> ACKNOWLEDGED -> DISPATCHED -> RESOLVED`. After update, also broadcast through SSE so other operators' screens stay synchronized in real time. |
| F-06 | Docker Compose | Start the full environment with one `docker compose up` command. |
| F-07 | Seed script | `python scripts/seed.py` continuously posts random events. |
| F-08 | Dashboard UI | Static HTML and vanilla JavaScript dashboard with real-time SSE updates. |
| F-09 | YOLO integration | Parse video with YOLOv8 and automatically send detections to `POST /events`. This is optional extra credit. |

## 03 API Endpoint Specification

| Method | Path | Purpose | Status |
| --- | --- | --- | --- |
| `POST` | `/events` | Event ingestion | `201 Created` |
| `GET` | `/events` | Event list | `200 OK` |
| `GET` | `/events/{id}` | Event detail | `200 / 404` |
| `PATCH` | `/events/{id}/status` | Status update | `200 OK` |
| `GET` | `/events/stream` | SSE long-lived connection | `200 text/event-stream` |

### Query Parameters - `GET /events`

| Parameter | Type | Example | Description |
| --- | --- | --- | --- |
| `severity` | string | `HIGH,CRITICAL` | Multiple values may be specified with commas. |
| `event_type` | string | `DEBRIS` | Single event type. |
| `status` | string | `NEW` | Single status. |
| `sort_by` | string | `detected_at` | `detected_at` or `severity`. |
| `order` | string | `desc` | `asc` or `desc`; default is `desc`. |
| `limit` | int | `20` | Default `20`, maximum `100`. |
| `offset` | int | `0` | Default `0`. |

### Unified Response Format

```json
{
  "success": true,
  "data": [],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

## 04 Data Model

### `incident_events` Table

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | UUID | Yes | Primary key, generated automatically. |
| `event_type` | enum | Yes | `STOPPED_VEHICLE`, `DEBRIS`, `CONGESTION`, `WRONG_WAY`, `PEDESTRIAN`, or `UNKNOWN`. |
| `severity` | enum | Yes | `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`. |
| `status` | enum | Auto | `NEW`, `ACKNOWLEDGED`, `DISPATCHED`, or `RESOLVED`; default is `NEW`. |
| `description` | text | No | AI-generated event description. |
| `confidence` | float | Yes | AI detection confidence from `0.0` to `1.0`. |
| `camera_id` | varchar | Yes | Camera ID. |
| `highway_id` | varchar | No | Road or route number, such as `E1` or `C2`. |
| `latitude` | float | Yes | Latitude. |
| `longitude` | float | Yes | Longitude. |
| `image_url` | varchar | No | Snapshot URL at detection time. |
| `detected_at` | timestamp | Yes | Timestamp assigned by the AI detector. |
| `ingested_at` | timestamp | Auto | Timestamp when the API receives the event; used for delay measurement. |
| `updated_at` | timestamp | Auto | Last update timestamp. |

`ingested_at - detected_at` is the detection delay. Showing this in the dashboard makes system health visible.

## 05 Non-Functional Requirements

| Item | Requirement | Implementation |
| --- | --- | --- |
| API documentation | Auto generated | FastAPI built-in Swagger UI at `/docs`. |
| Validation | Validate all fields | Pydantic v2. |
| Error handling | Explicit `400/404/422/500` handling | FastAPI exception handlers. |
| Environment settings | `.env` management | `python-dotenv`. |
| Code structure | Layered architecture | `router / service / repository / schema`. |
| Authentication | Out of scope | State in README that production should use API key or JWT bearer token. |
| Tests | Main endpoints | `pytest` and `httpx`. |

Authentication and authorization are outside the test scope. The README should clearly state that production would require API Key or JWT Bearer Token.

## 06 YOLO Dataset Selection

| Scenario | Main dataset | Format | Strategy | Fine-tune |
| --- | --- | --- | --- | --- |
| Stopped vehicle on shoulder | BDD100K + MIO-TCD | JSON converted to YOLO txt | Vehicle detection + ByteTrack + shoulder ROI dwell-time rule. | Required |
| Road debris | RAOD (UnicomAI) | Mask converted to bbox | YOLOv8-seg and synthetic copy-paste augmentation. | Strongly required |
| Abnormal congestion | TRANCOS + Mendeley congestion dataset | YOLO txt | Density count + speed estimation + threshold rule. | Required |

### Model Selection

| Scenario | Model | Input size | Notes |
| --- | --- | --- | --- |
| Stopped vehicle | `yolov8m.pt` | `640x640` | Used with ByteTrack tracking. |
| Road debris | `yolov8m-seg.pt` | `1280x1280` | Higher resolution for small objects. |
| Abnormal congestion | `yolov8s.pt` | `640x640` | Speed-first, counting-focused. |

## 07 Directory Structure

```text
traffic-incident-api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   └── incident.py
│   ├── schemas/
│   │   └── incident.py
│   ├── routers/
│   │   ├── incidents.py
│   │   └── stream.py
│   └── services/
│       ├── incident_service.py
│       └── sse_manager.py
├── scripts/
│   └── seed.py
├── yolo/
│   └── detector.py
├── ui/
│   └── index.html
├── tests/
│   └── test_incidents.py
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 08 Implementation Steps

### Phase 1 - Backend API, Day 1-2

1. Initialize the project structure and dependency list.
2. Define SQLAlchemy ORM models, enums, SQLite connection, and `Base.metadata.create_all()`.
3. Define Pydantic schemas: `IncidentCreate`, `IncidentResponse`, and a unified `APIResponse`.
4. Implement `POST /events` through router, service, and repository layers; broadcast through SSE after saving.
5. Implement `PATCH /events/{id}/status`; always broadcast status updates with `type: "STATUS_UPDATE"`.
6. Implement `GET /events` and `GET /events/{id}` with filters, sorting, pagination, and total count.
7. Implement the SSE endpoint with `asyncio.Queue`.
8. Add tests with `pytest` and `httpx.AsyncClient`, including `422` validation and `404` not-found cases.

### Phase 2 - YOLO Integration, Day 3-4

Risk control: only start this after Phase 1, 3, and 4 are fully completed. If time is short, skip fine-tuning and run a demo with `yolov8n.pt` trained on COCO. The interviewer evaluates end-to-end system integration more than model accuracy.

Minimum demo:

1. Run `yolov8n.pt` against any highway video.
2. Detect `car` and post it as a `STOPPED_VEHICLE` event.
3. Treat end-to-end API integration as sufficient if fine-tuning is not ready.

If time allows:

1. Road debris: convert RAOD masks to bounding boxes and fine-tune YOLOv8 segmentation.
2. Stopped vehicle: fine-tune with BDD100K / MIO-TCD, track with ByteTrack, define shoulder ROI, and fire event after N seconds of dwell time.
3. Abnormal congestion: train a vehicle counter with TRANCOS / Mendeley, calculate ROI density and average speed, then fire `CONGESTION` when thresholds are exceeded.
4. Integrate all detections with `POST /events`.

### Phase 3 - Infrastructure, Day 4

1. Add a Dockerfile based on `python:3.11-slim`.
2. Add `docker-compose.yml` with API service and persistent SQLite volume.
3. Add a seed script that randomly generates the three event types every 2 to 5 seconds using coordinates around Japanese expressways.

### Phase 4 - Dashboard UI, Day 5

1. Build a static HTML dashboard with filters for `severity`, `event_type`, and `status`.
2. Render event cards with `detected_at`, `severity`, location, and description.
3. Color-code by severity.
4. Connect to SSE and use a `Set` of rendered IDs to avoid duplicate rendering between initial load and SSE push.
5. On `STATUS_UPDATE`, update the existing card instead of adding a new one.
6. Show `ingested_at - detected_at` as detection delay for each event.

## 09 Out Of Scope

| Item | Production approach |
| --- | --- |
| Authentication and authorization | API Key or JWT Bearer. |
| Rate limiting | Nginx or API Gateway. |
| Image storage | S3 / CloudFront. |
| Production database | PostgreSQL. |
| HTTPS / TLS | Nginx reverse proxy. |
| YOLO model accuracy guarantee | Requires production data collection and fine-tuning. |
