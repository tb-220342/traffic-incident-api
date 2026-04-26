# Implementation vs Requirements v2

Languages: [English](implementation-vs-requirements-v2.en.md) | [日本語](implementation-vs-requirements-v2.ja.md) | [繁體中文](implementation-vs-requirements-v2.md)

Back to [Document Index](document-index.md)

Last updated: 2026-04-26 (Asia/Tokyo)

> [!IMPORTANT]
> Current status: required backend scope is complete, demo enhancements are complete, and YOLO integration is demo-ready with public-safe artifacts.

## Verification Snapshot

- `pytest`: `7 passed`
- `docker compose up -d --build`: verified
- Docker `/health`: `200 OK`
- `POST /events`:
  - first create: `201 Created`
  - same `source_event_id` and identical payload: `200 OK` + `meta.deduplicated=true`
  - same `source_event_id` with conflicting payload: `409 Conflict`
- `GET /events/stream`: `200 text/event-stream`
- Dashboard:
  - `/ui/` returns `200`
  - front-end calls `/events`
  - SSE connects through `/events/stream`
  - language switch supports English / Japanese / Chinese

## Completion Checklist

### P0 Mandatory Scope

| Item | Status | Notes |
| --- | --- | --- |
| `POST /events` ingest | Complete | Supports validation, idempotency, `source_event_id` dedup, `201/200/409` behavior |
| `GET /events` list API | Complete | Supports `severity`, `event_type`, `status`, `camera_id`, `highway_id`, sorting, pagination |
| `GET /events/{id}` detail API | Complete | Supports `404 NOT_FOUND` |
| `PATCH /events/{id}/status` | Complete | Enforces allowed workflow transitions, supports rollback for operator mistakes, no-op updates, and `409 INVALID_STATUS_TRANSITION` for unsupported jumps |
| `GET /events/stream` SSE | Complete | Emits `incident.created`, `incident.status_updated`, plus keep-alive messages |
| SQLite persistence | Complete | Used locally and in Docker with lightweight migration logic |
| Unified response format | Complete | Uses `success/data/meta` and `success/error` |
| UTC timestamps | Complete | `detected_at`, `ingested_at`, and `updated_at` are normalized to UTC and serialized with `Z` |
| Basic structured logging | Complete | Logs requests, SSE connections, event creation, deduplication, and status updates |
| README and AI log | Complete | README and AI workflow log are included |

### P1 Demo Enhancements

| Item | Status | Notes |
| --- | --- | --- |
| One-command Docker startup | Complete | `api` and `seed` services start through Docker Compose |
| Fake event generator | Complete | `scripts/seed.py` continuously posts valid events |
| Dashboard | Complete | Shows searchable event results, details, delay, reversible status actions, and SSE updates |
| Dashboard language switch | Complete | Supports English / Japanese / Chinese |
| Dashboard usability improvements | Complete | Search-only filter explanation, direct page jump, rows-per-page control, localized incident titles, dropdown enum filters, manual text/range filters, field tooltips, and confirmation before status changes |
| KPI and delay display | Complete | Shows page / matching totals for displayed count, critical count, and average delay; last card shows search time and DB update time |

### P2 YOLO / Video Integration

| Item | Status | Notes |
| --- | --- | --- |
| `infer_video.py` posts incidents to the API | Complete | Verified on 2026-04-26 with `rdd_damage_short.mp4`; two `DEBRIS` events were inserted from `CAM-YOLO-VIDEO-RDD` |
| Trained weights retained locally | Complete | MIO, RDD2022, and TRANCOS runs are kept under `<DATA_ROOT>\runs`; public repo keeps only training summaries in `model-artifacts/`, not `.pt` weights |
| External storage for ML assets | Complete | Datasets, cache, runs, and snapshots default to `../traffic-incident-data` and can be overridden with `TRAFFIC_DATASETS_ROOT` |
| End-to-end video quality check | Demo-ready / manual review | Two short test clips and YOLO box outputs are kept locally under `<DATA_ROOT>\yolovideotest`; the public repo excludes dataset-derived MP4/snapshot files but retains the verified API events in the demo DB |

## Remaining Manual Checks

- Open `http://127.0.0.1:8000/ui/` and visually inspect the Dashboard.
- Switch `EN / 日本語 / 中文` and confirm labels, incident titles, event tags, and status buttons update.
- Confirm the filter area reads as search-only, not data registration or editing.
- Confirm the top KPIs change with the active filters and show page / matching totals.
- Confirm the last KPI shows search time and DB update time.
- Change rows per page, type a page number, click Go / Previous / Next, and confirm the result range and cards update.
- Try advanced filters for camera/location, camera ID, source event ID, detected/received time, delay seconds, and confidence.
- Hover labels and field names to see explanations for severity, event type, status, delay, location, coordinates, source ID, and camera ID.
- Click a status button in the Dashboard, then move it back and confirm both directions update correctly.
- If YOLO is part of the demo, run it with a real road video and review false positives / false negatives.
- Before pushing to GitHub, confirm that no raw/prepared training images, MP4 clips, snapshots, `.pt` weights, caches, secrets, or intermediate epoch checkpoints are staged.

## How To Run

### Docker

```powershell
cd <repo-root>
docker compose up -d --build
docker compose ps
```

Open:

- Swagger: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8000/ui/`

Stop seed data if you want a quiet manual test:

```powershell
docker compose stop seed
```

Shut everything down:

```powershell
docker compose down
```

### Local API

```powershell
cd <repo-root>
.\.venv\Scripts\uvicorn app.main:app --reload
```

### Tests

```powershell
cd <repo-root>
.\.venv\Scripts\pytest
```

## Manual API Checks

Create an event through Swagger or another API client:

```json
{
  "source_event_id": "manual-check-001",
  "event_type": "DEBRIS",
  "severity": "HIGH",
  "description": "Manual verification payload",
  "confidence": 0.88,
  "camera_id": "CAM-MANUAL-001",
  "highway_id": "E1",
  "road_marker": "K10+500",
  "lane_no": "1",
  "detected_at": "2026-04-23T10:00:00+09:00"
}
```

Expected:

- `201 Created`
- optional coordinates return as `null`
- `meta.deduplicated = false`
- `detected_at` is normalized to UTC, for example `2026-04-23T01:00:00Z`

Dedup check:

- send the same body again
- expect `200 OK`, `meta.deduplicated=true`, and the same `id`

Conflict check:

- keep the same `source_event_id`
- change a core field such as `severity`
- expect `409 DUPLICATE_CONFLICT`

SSE check:

```powershell
curl.exe -N http://127.0.0.1:8000/events/stream
```

Expected event names:

- `incident.created`
- `incident.status_updated`

## YOLO Check

Vehicle / stopped-vehicle / congestion:

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode vehicle `
  --weights <DATA_ROOT>\runs\mio-localization\mio-stage2-20260421-234643\weights\best.pt `
  --source <path-to-highway-video>.mp4 `
  --base-url http://127.0.0.1:8000
```

Road anomaly / debris:

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source <path-to-road-video>.mp4 `
  --base-url http://127.0.0.1:8000
```
