# Architecture Review Notes

Languages: [English](architecture-review-notes.md) | [日本語](architecture-review-notes.ja.md) | [繁體中文](architecture-review-notes.zh-Hant.md)

[Back to Documentation Index](document-index.md) | [Project README](../README.md)

> [!NOTE]
> This note maps the implementation to the main evaluation points in the back-end assignment: API design, schema/data model design, real-time delivery, trade-offs, and production follow-up.

## 1. API Design

The API follows the event lifecycle in the assignment scenario: a detection system creates an incident, operators query it, and operators update its response status.

| Endpoint | Reasoning |
| --- | --- |
| `POST /events` | Ingests detection events from the AI/video analysis side. The endpoint validates input with Pydantic and persists accepted events. |
| `GET /events` | Provides the operator-facing event list with filtering, sorting, and pagination. This directly supports dispatch-center search and triage workflows. |
| `GET /events/{id}` | Returns a single incident for detail inspection. |
| `PATCH /events/{id}/status` | Models the operator workflow after an incident is reviewed. Status can move forward or backward to support correction of mistaken actions. |
| `GET /events/stream` | Streams new events and status changes to dashboard clients. |

`source_event_id` is used as an idempotency key. This is important because detection systems, message pipelines, or retry logic may send the same event more than once. Same payload + same `source_event_id` is treated as a safe duplicate; conflicting payloads return `409 Conflict`.

## 2. Data Model

The data model is intentionally compact but operationally useful. It stores enough information for a dispatcher to understand what happened, where it happened, how urgent it is, and how reliable the detection is.

| Field group | Design reason |
| --- | --- |
| Identity | `id` is an internal UUID. `source_event_id` links back to the detection source and enables idempotency. |
| Incident type | `event_type` captures stopped vehicle, debris, congestion, wrong-way driving, pedestrian detection, and similar categories. |
| Priority | `severity` lets the operator and API prioritize urgent events. |
| Operator workflow | `status`, `status_note`, `updated_at` support incident handling and auditability. |
| Time | `detected_at` and `ingested_at` are separated so the system can measure detection-to-API delay. |
| Location | `camera_id`, `highway_id`, `road_marker`, `lane_no`, latitude, and longitude support both human review and future map integration. |
| Evidence | `description`, `image_url`, and `extra_payload` preserve context without overfitting the schema too early. |
| ML confidence | `confidence` keeps the detector score visible so low-confidence events can be reviewed with caution. |

Latitude and longitude are optional because some traffic systems identify incidents by camera, road marker, or lane instead of GPS. This keeps the API practical for both structured map data and camera-based operations.

## 3. Real-Time Notification

The assignment says speed matters: the sooner operators see an incident, the sooner they can respond. The implementation uses Server-Sent Events (SSE) for this reason.

SSE is a good fit because the main real-time flow is one-way: server to dashboard. The dashboard needs to receive `incident.created` and `incident.status_updated` events, but it does not need a full bidirectional WebSocket channel.

Why SSE over polling:

- Polling adds delay and unnecessary repeated requests.
- SSE pushes events as soon as the API accepts or updates them.
- SSE is simple to run in a demo environment and easy to inspect from a browser or terminal.

Why SSE over WebSocket:

- WebSocket is useful for complex bidirectional interaction.
- This assignment mainly needs one-way operational updates.
- SSE keeps the architecture smaller while still answering the speed requirement.

## 4. SQLite Choice

SQLite is a deliberate assignment/demo choice, not a claim that SQLite is the best production database for this domain.

It is reasonable here because:

- The assignment explicitly says even SQLite is fine for this exercise.
- Reviewers can clone the repository and run the service without provisioning a database server.
- Docker Compose can persist the SQLite file through a mounted volume.
- The data model and repository layer can later move to PostgreSQL without changing the public API contract.

The trade-off is that SQLite is not ideal for a high-write, multi-instance production deployment. That limitation is documented and treated as a production follow-up.

## 5. Production Follow-Up

For production, the next steps would be:

| Area | Production improvement |
| --- | --- |
| Database | Replace SQLite with PostgreSQL and add Alembic migrations. |
| Reliability | Put event ingestion behind a queue or stream when detector traffic increases. |
| Authentication | Add API keys, OAuth, or service-to-service authentication for detection systems and operators. |
| Authorization | Separate detector write permissions from operator read/update permissions. |
| Observability | Add metrics, tracing, structured logs, and alerting for ingestion latency and SSE failures. |
| Scalability | Use Redis, PostgreSQL LISTEN/NOTIFY, or a message broker for multi-instance SSE broadcast. |
| Operations | Add backup, retention policy, deployment pipeline, and incident-response runbook. |
| ML integration | Version models and datasets, store inference provenance, and monitor false positives/false negatives. |

## Summary

The current architecture is intentionally scoped for the interview assignment: it is small, runnable, and end-to-end demonstrable. The API and data model match the traffic-incident workflow, SSE addresses the speed requirement, SQLite keeps review friction low, and the production gaps are explicit rather than hidden.
