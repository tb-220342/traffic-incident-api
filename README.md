# Traffic Incident Monitoring API Platform

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](#tech-choices)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](#api-endpoints)
[![SQLite](https://img.shields.io/badge/SQLite-Persistence-003B57?logo=sqlite&logoColor=white)](#local-run)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](#docker-run)
[![SSE](https://img.shields.io/badge/Realtime-SSE-111827)](#response-contract-highlights)
[![YOLO](https://img.shields.io/badge/YOLO-Optional%20Pipeline-FF6B00)](#yolo-training-version)

Language: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-Hant.md)

Back-end interview project for a traffic incident monitoring platform. It ingests AI-generated road incidents, stores them in SQLite, exposes queryable REST APIs, and pushes real-time dashboard updates with Server-Sent Events.

> [!NOTE]
> The repository is public-release safe. Raw datasets, dataset-derived MP4 files, snapshots, trained `.pt` weights, local `.env`, and machine-specific paths are intentionally excluded.

## Reviewer Quick Path

| Goal | Link / Command |
| --- | --- |
| Run the demo | `docker compose up -d --build` |
| Open API docs | `http://127.0.0.1:8000/docs` |
| Open dashboard | `http://127.0.0.1:8000/ui/` |
| Check implementation coverage | [Implementation vs Requirements](docs/implementation-vs-requirements-v2.en.md) |
| Read deployment guide | [Deployment](docs/deployment.md) |
| Review all documents | [Document Index](docs/document-index.md) |

## Document Hub

| Document | English | Japanese | Chinese |
| --- | --- | --- | --- |
| Document index | [EN](docs/document-index.md) | [JA](docs/document-index.ja.md) | [ZH](docs/document-index.zh-Hant.md) |
| Deployment guide | [EN](docs/deployment.md) | [JA](docs/deployment.ja.md) | [ZH](docs/deployment.zh-Hant.md) |
| Implementation status | [EN](docs/implementation-vs-requirements-v2.en.md) | [JA](docs/implementation-vs-requirements-v2.ja.md) | [ZH](docs/implementation-vs-requirements-v2.md) |
| Requirements specification | [EN](docs/requirements-spec.en.md) | [JA](docs/requirements-spec.ja.md) | [ZH](docs/requirements-spec.zh-Hant.md) |
| AI workflow log | [EN](docs/ai-log.md) | [JA](docs/ai-log.ja.md) | [ZH](docs/ai-log.zh-Hant.md) |
| AI conversation source | [EN](docs/ai-conversation-source.en.md) | [JA](docs/ai-conversation-source.ja.md) | [ZH](docs/ai-conversation-source.zh-Hant.md) |
| YOLO video test | [EN](docs/yolo-video-test.md) | [JA](docs/yolo-video-test.ja.md) | [ZH](docs/yolo-video-test.zh-Hant.md) |
| Assets and sources | [EN](docs/submission-assets.md) | [JA](docs/submission-assets.ja.md) | [ZH](docs/submission-assets.zh-Hant.md) |
| Public release notes | [EN](docs/public-release-notes.md) | [JA](docs/public-release-notes.ja.md) | [ZH](docs/public-release-notes.zh-Hant.md) |

Original source files: [requirements PDF](docs/requirements_spec.md.pdf), [AI conversation PDF](docs/Claude_geminiconversation.md.pdf), [raw extracted AI conversation](docs/ai-conversation-source.md).

## What Is Included

| Area | Highlights |
| --- | --- |
| API | FastAPI, Pydantic validation, idempotent `source_event_id` ingest, list/detail/status endpoints |
| Realtime | SSE stream for `incident.created` and `incident.status_updated` |
| Persistence | SQLAlchemy + SQLite with Docker volume persistence |
| Dashboard | Vanilla JS UI, EN/JA/ZH switching, filter guidance, pagination, tooltips, reversible status actions |
| Demo Ops | Docker Compose, seed script, Swagger UI, packaged demo database |
| YOLO Extension | Download, prepare, train, infer, and post detections back to the API |
| Evidence | Tests, screenshots, AI logs, requirement comparison, public-release notes |

## Tech choices

- **FastAPI**: automatic docs, fast iteration, native async support
- **SQLite**: sufficient for the exercise, simple local setup
- **SQLAlchemy 2.x**: explicit data model and query control
- **SSE**: direct answer to the “Speed matters” requirement without introducing unnecessary infrastructure
- **Vanilla JS dashboard**: lightweight demo UI with no framework overhead

## Project structure

```text
traffic-incident-api/
├── app/
│   ├── core/
│   ├── models/
│   ├── repositories/
│   ├── routers/
│   ├── schemas/
│   └── services/
├── docs/
├── scripts/
├── tests/
├── ui/
├── yolo/
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/events` | Create a new incident event |
| `GET` | `/events` | List incidents with filtering, sorting, pagination |
| `GET` | `/events/{id}` | Retrieve one incident |
| `PATCH` | `/events/{id}/status` | Move status forward or backward in the operator workflow |
| `GET` | `/events/stream` | Subscribe to real-time incident updates over SSE |

### Supported filters

- `severity=HIGH,CRITICAL`
- `event_type=DEBRIS,CONGESTION`
- `status=NEW,ACKNOWLEDGED`
- `camera_query=CAM,E1,K12+300` for camera/location keyword search
- `camera_id=CAM-001`
- `source_event_id=producer-id`
- `highway_id=E1`
- `detected_from`, `detected_to`, `ingested_from`, `ingested_to` as ISO datetimes
- `min_delay_seconds`, `max_delay_seconds`
- `min_confidence`, `max_confidence` as `0.0..1.0`
- `sort_by=detected_at|ingested_at|updated_at|severity|confidence|detection_delay`
- `order=asc|desc`
- `limit=1..100`
- `offset=0..`

## Local run

### 1. Create a virtual environment

```bash
python -m venv .venv
```

### 2. Install dependencies

```bash
.venv\Scripts\pip install -r requirements.txt
```

### 3. Start the API

```bash
.venv\Scripts\uvicorn app.main:app --reload
```

### 4. Open the dashboard

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8000/ui/`

### 5. Generate demo traffic incidents

```bash
.venv\Scripts\python scripts\seed.py
```

## Docker run

```bash
docker compose up --build
```

This starts:

- `api` on port `8000`
- `seed` which continuously posts random incidents to the API

## Example event payload

```json
{
  "source_event_id": "cam-001-track-981-2026-04-23T08:30:12Z",
  "event_type": "DEBRIS",
  "severity": "HIGH",
  "description": "Road debris detected on lane 1 shoulder",
  "confidence": 0.94,
  "camera_id": "CAM-001",
  "highway_id": "E1",
  "road_marker": "K12+300",
  "lane_no": "2",
  "latitude": 35.68,
  "longitude": 139.76,
  "image_url": "https://example.com/incidents/1.jpg",
  "detected_at": "2026-04-20T08:00:00Z",
  "extra_payload": {
    "model": "seed"
  }
}
```

## Response contract highlights

- `POST /events` returns `201` on first create
- `POST /events` returns `200` with `meta.deduplicated=true` when the same `source_event_id` is resent with identical content
- duplicate `source_event_id` with conflicting content returns `409`
- `PATCH /events/{id}/status` returns `200` with `meta.noop=true` if the requested status already matches the current status
- SSE emits named events:
  - `incident.created`
  - `incident.status_updated`

## Testing

```bash
.venv\Scripts\pytest
```

Detailed implementation status and manual verification steps are in `docs/implementation-vs-requirements-v2.md`.

## YOLO training version

The project now includes a training-oriented `yolo/` pipeline. Large datasets, caches, checkpoints, and snapshots are written outside the repository by default, under `../traffic-incident-data`, or to the path configured by `TRAFFIC_DATASETS_ROOT`.

In the examples below, `<DATA_ROOT>` refers to that external ML data directory.

### 1. Install the ML stack

```powershell
.\scripts\setup_training_env.ps1
```

This installs:

- CUDA-enabled `torch` / `torchvision` / `torchaudio`
- `ultralytics`
- OpenCV and image-processing dependencies

### 2. Download official datasets

```powershell
.\.venv\Scripts\python.exe -m yolo.download_datasets --show-paths
```

Default dataset targets:

- `mio-localization`: official MIO-TCD localization set
- `rdd2022`: official CRDDC RDD2022 archive
- `trancos`: official TRANCOS package

### 3. Prepare datasets for YOLO

```powershell
.\.venv\Scripts\python.exe -m yolo.prepare_mio_tcd
.\.venv\Scripts\python.exe -m yolo.prepare_rdd2022
```

### 4. Train models

```powershell
.\.venv\Scripts\python.exe -m yolo.train --profile mio-localization
.\.venv\Scripts\python.exe -m yolo.train --profile rdd2022
```

### 5. Feed trained detections back into the API

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode vehicle --weights <DATA_ROOT>\runs\mio-localization\<run>\weights\best.pt --source <path-to-highway-video>.mp4
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights <DATA_ROOT>\runs\rdd2022\<run>\weights\best.pt --source <path-to-road-video>.mp4
```

`vehicle` mode turns tracked detections into `STOPPED_VEHICLE` and `CONGESTION` events.  
`damage` mode maps road-surface anomalies into `DEBRIS` events.
Use `--annotated-output <output-video>.boxes.mp4` to export a video with YOLO boxes. Use `--dry-run` when you want to inspect detection quality without writing events to the API.

Short local test clips can be generated under `<DATA_ROOT>\yolovideotest`. For public GitHub release, dataset-derived MP4 files, snapshots, and trained `.pt` weights are not committed. The RDD demo clip was verified locally without `--dry-run`; it inserted two `DEBRIS` events through `POST /events` using `camera_id=CAM-YOLO-VIDEO-RDD`.

Local dry-run demo example after regenerating or restoring local weights and test clips:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt --source <DATA_ROOT>\yolovideotest\rdd_damage_short.mp4 --annotated-output <DATA_ROOT>\yolovideotest\rdd_damage_short.boxes.mp4 --dry-run
```

### 6. YOLO-to-API-to-database demo

This is the shortest reviewer-friendly path for proving that YOLO detections can be converted into API events and persisted in SQLite. It requires local dataset-derived clips and trained weights, which are excluded from the public repository for licensing safety.

1. Start the API:

```powershell
cd <repo-root>
docker compose up -d --build
docker compose stop seed
```

2. Run the local RDD2022 clip without `--dry-run`:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source <DATA_ROOT>\yolovideotest\rdd_damage_short.mp4 `
  --base-url http://127.0.0.1:8000 `
  --camera-id CAM-YOLO-VIDEO-RDD `
  --highway-id E1 `
  --confidence 0.25 `
  --frame-stride 1 `
  --cooldown-seconds 5 `
  --annotated-output <DATA_ROOT>\yolovideotest\rdd_damage_short.boxes.mp4
```

Expected terminal output includes:

```text
[frame 0] reported DEBRIS with labels D00
[frame 50] reported DEBRIS with labels D00
```

3. Query the events written by YOLO:

```powershell
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' |
  ConvertTo-Json -Depth 12
```

You should see `event_type=DEBRIS`, `camera_id=CAM-YOLO-VIDEO-RDD`, and `extra_payload.source=yolo.detector`. The same records can be checked in Swagger at `http://127.0.0.1:8000/docs` through `GET /events`, or in the dashboard at `http://127.0.0.1:8000/ui/` by filtering `Camera ID` with `CAM-YOLO-VIDEO-RDD`.

## Trade-offs and assumptions

- Authentication and authorization are intentionally out of scope for this assignment.
- SQLite is chosen for simplicity; production should move to PostgreSQL.
- SSE is used instead of WebSockets because the current requirement is one-way server-to-dashboard delivery.
- Status transitions are enforced with explicit workflow rules, while common rollback paths are allowed for operator mistakes.
- `source_event_id` is the idempotency key between detector-side producers and the API.
- The dashboard focuses on operational visibility rather than polished product UX.
- The vehicle detector is fine-tuned on MIO-TCD because it is directly available and suitable for stopped-vehicle and congestion heuristics.
- `RDD2022` is used as the closest openly downloadable road-anomaly training source; it maps to `DEBRIS` events as a roadway hazard proxy, not a perfect debris taxonomy match.
- `TRANCOS` is downloaded for congestion-threshold calibration and future counting-specific work, but the main congestion event flow currently reuses the fine-tuned MIO vehicle detector.
- Raw training images, dataset-derived demo videos/snapshots, trained `.pt` weights, and intermediate epoch checkpoints are intentionally excluded from the public Git repository. The code and scripts remain sufficient to reproduce them locally after obtaining the datasets under their original terms.

## Production follow-ups

- Add API key or JWT-based authentication
- Introduce rate limiting and audit logging
- Store images in object storage such as S3
- Move persistence to PostgreSQL
- Add background workers and retry queues for upstream detector ingest
- Add calibrated model evaluation and monitoring for the detector pipeline
