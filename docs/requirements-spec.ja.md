# 要件定義書 - Traffic Incident Monitoring API Platform

言語: [English](requirements-spec.en.md) | [日本語](requirements-spec.ja.md) | [繁體中文](requirements-spec.zh-Hant.md)

原 PDF: [requirements_spec.md.pdf](requirements_spec.md.pdf)

これは Back-End Candidate Evaluation 向けに作成した要件定義書の日本語整形版です。

## 01 プロジェクト概要

| 項目 | 内容 |
| --- | --- |
| システム名 | Traffic Incident Monitoring API Platform |
| 目的 | AI 動画解析が検出した事故・異常イベントを受信し、管制センターへほぼリアルタイムに配信する。 |
| 対象ユーザー | 高速道路オペレーションセンターのスタッフ。 |
| 提出形式 | Git リポジトリ、README、AI 対話ログ。 |
| 技術制約 | なし。言語、フレームワーク、依存関係は自由。 |

設計思想は **Speed matters**。SSE によるリアルタイム push で、検出から画面表示までの遅延を最小化する。

## 02 機能要件

### 必須

| ID | Endpoint | 内容 |
| --- | --- | --- |
| F-01 | `POST /events` | AI 検出システムから event を受信する。Pydantic で request を検証し、受信後すぐ SSE で broadcast する。 |
| F-02 | `GET /events` | event 一覧を取得する。`severity`、`event_type`、`status` の filter、`detected_at` / `severity` の sort、pagination に対応する。 |
| F-03 | `GET /events/{id}` | 単一 event を取得する。存在しない場合は `404` を返す。 |

### 推奨 / Nice To Have

| ID | 機能 | 内容 |
| --- | --- | --- |
| F-04 | `GET /events/stream` | SSE の長期接続。`POST /events` のたびに全 Dashboard へ即時配信し、"Speed matters" に直接答える。 |
| F-05 | `PATCH /events/{id}/status` | `NEW -> ACKNOWLEDGED -> DISPATCHED -> RESOLVED` の status 更新。更新後も SSE broadcast を発火し、他オペレーターの画面を同期する。 |
| F-06 | Docker Compose | `docker compose up` 一つで環境全体を起動する。 |
| F-07 | Seed Script | `python scripts/seed.py` で random event を継続 POST する。 |
| F-08 | Dashboard UI | 静的 HTML + vanilla JavaScript。SSE でリアルタイム更新する。 |
| F-09 | YOLO 連携 | YOLOv8 で動画解析し、検出結果を `POST /events` に自動送信する。自選加点要素。 |

## 03 API Endpoint 仕様

| Method | Path | 用途 | Status |
| --- | --- | --- | --- |
| `POST` | `/events` | event 受信 | `201 Created` |
| `GET` | `/events` | 一覧取得 | `200 OK` |
| `GET` | `/events/{id}` | 単一取得 | `200 / 404` |
| `PATCH` | `/events/{id}/status` | status 更新 | `200 OK` |
| `GET` | `/events/stream` | SSE 長期接続 | `200 text/event-stream` |

### Query Parameters - `GET /events`

| Parameter | Type | Example | 説明 |
| --- | --- | --- | --- |
| `severity` | string | `HIGH,CRITICAL` | カンマ区切りで複数指定可能。 |
| `event_type` | string | `DEBRIS` | 単一 event type。 |
| `status` | string | `NEW` | 単一 status。 |
| `sort_by` | string | `detected_at` | `detected_at` または `severity`。 |
| `order` | string | `desc` | `asc` または `desc`。default は `desc`。 |
| `limit` | int | `20` | default `20`、最大 `100`。 |
| `offset` | int | `0` | default `0`。 |

### 統一 Response Format

```json
{
  "success": true,
  "data": [],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

## 04 データモデル

### `incident_events` Table

| Field | Type | 必須 | 説明 |
| --- | --- | --- | --- |
| `id` | UUID | Yes | 主キー。自動生成。 |
| `event_type` | enum | Yes | `STOPPED_VEHICLE`、`DEBRIS`、`CONGESTION`、`WRONG_WAY`、`PEDESTRIAN`、`UNKNOWN`。 |
| `severity` | enum | Yes | `LOW`、`MEDIUM`、`HIGH`、`CRITICAL`。 |
| `status` | enum | Auto | `NEW`、`ACKNOWLEDGED`、`DISPATCHED`、`RESOLVED`。default は `NEW`。 |
| `description` | text | No | AI が生成した event description。 |
| `confidence` | float | Yes | AI detection confidence。`0.0` から `1.0`。 |
| `camera_id` | varchar | Yes | Camera ID。 |
| `highway_id` | varchar | No | 路線番号。例: `E1`、`C2`。 |
| `latitude` | float | Yes | 緯度。 |
| `longitude` | float | Yes | 経度。 |
| `image_url` | varchar | No | 検出時 snapshot URL。 |
| `detected_at` | timestamp | Yes | AI 側が設定する検出時刻。 |
| `ingested_at` | timestamp | Auto | API が受信した時刻。遅延計測に使用。 |
| `updated_at` | timestamp | Auto | 最終更新時刻。 |

`ingested_at - detected_at` が検出遅延。Dashboard に表示することで system health を可視化できる。

## 05 非機能要件

| 項目 | 要件 | 実現方法 |
| --- | --- | --- |
| API documentation | 自動生成 | FastAPI built-in Swagger UI at `/docs`。 |
| Validation | 全 field 検証 | Pydantic v2。 |
| Error handling | `400/404/422/500` を明示 | FastAPI exception handler。 |
| Environment settings | `.env` 管理 | `python-dotenv`。 |
| Code structure | 分層 architecture | `router / service / repository / schema`。 |
| Authentication | Scope 外 | README に production では API key / JWT bearer が必要と明記。 |
| Tests | 主要 endpoint | `pytest` + `httpx`。 |

認証・認可はこの test scope 外。本番では API Key または JWT Bearer Token が必要。

## 06 YOLO Dataset 選定

| Scenario | Main dataset | Format | Strategy | Fine-tune |
| --- | --- | --- | --- | --- |
| 路肩停車 | BDD100K + MIO-TCD | JSON を YOLO txt に変換 | 車両検出 + ByteTrack + shoulder ROI 滞在時間 rule。 | 必須 |
| 路面 debris | RAOD (UnicomAI) | mask を bbox に変換 | YOLOv8-seg + synthetic copy-paste augmentation。 | 強く必須 |
| 異常渋滞 | TRANCOS + Mendeley congestion dataset | YOLO txt | 密度 count + speed estimation + threshold rule。 | 必須 |

### Model Selection

| Scenario | Model | Input size | Notes |
| --- | --- | --- | --- |
| 路肩停車 | `yolov8m.pt` | `640x640` | ByteTrack tracking と併用。 |
| 路面 debris | `yolov8m-seg.pt` | `1280x1280` | 小物体向けに高解像度。 |
| 異常渋滞 | `yolov8s.pt` | `640x640` | speed 優先、counting 重視。 |

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

## 08 実装ステップ

### Phase 1 - Backend API, Day 1-2

1. project structure と dependency list を初期化する。
2. SQLAlchemy ORM model、enum、SQLite connection、`Base.metadata.create_all()` を定義する。
3. `IncidentCreate`、`IncidentResponse`、統一 `APIResponse` を定義する。
4. router / service / repository 分層で `POST /events` を実装し、保存後に SSE broadcast する。
5. `PATCH /events/{id}/status` を実装し、`type: "STATUS_UPDATE"` 付きで必ず status update を broadcast する。
6. filter、sort、pagination、total count 付きで `GET /events` と `GET /events/{id}` を実装する。
7. `asyncio.Queue` を使って SSE endpoint を実装する。
8. `pytest` と `httpx.AsyncClient` で主要 endpoint、`422` validation、`404` not found を test する。

### Phase 2 - YOLO Integration, Day 3-4

Risk control: Phase 1 / 3 / 4 が 100% 完成してから着手する。時間が足りなければ fine-tune は省略し、COCO 事前学習の `yolov8n.pt` で demo を動かすだけでよい。面接官が見るのは model accuracy より end-to-end system integration。

Minimum demo:

1. 任意の高速道路 video を `yolov8n.pt` で解析する。
2. `car` を検出し、`STOPPED_VEHICLE` event として POST する。
3. fine-tune が未完成でも、API 連携が end-to-end で成立すれば十分。

時間があれば:

1. 路面 debris: RAOD mask を bbox に変換し、YOLOv8 segmentation を fine-tune。
2. 路肩停車: BDD100K / MIO-TCD で fine-tune、ByteTrack tracking、shoulder ROI、N 秒滞在で event 発火。
3. 異常渋滞: TRANCOS / Mendeley で vehicle counter を学習し、ROI density と average speed で `CONGESTION` を発火。
4. 全 detection を `POST /events` と統合する。

### Phase 3 - Infrastructure, Day 4

1. `python:3.11-slim` based Dockerfile を追加する。
2. API service と persistent SQLite volume を持つ `docker-compose.yml` を追加する。
3. 日本の高速道路付近の座標を使い、3 種類の event を 2-5 秒ごとに random 生成する seed script を追加する。

### Phase 4 - Dashboard UI, Day 5

1. `severity`、`event_type`、`status` filter を持つ static HTML dashboard を作る。
2. `detected_at`、`severity`、location、description を event card に表示する。
3. severity ごとに color coding する。
4. 初期 load と SSE push の race condition で重複表示しないよう、rendered ID の `Set` を使う。
5. `STATUS_UPDATE` では新規 card を追加せず、既存 card を更新する。
6. 各 event に `ingested_at - detected_at` の detection delay を表示する。

## 09 Scope 外

| Item | Production approach |
| --- | --- |
| Authentication / Authorization | API Key または JWT Bearer。 |
| Rate limiting | Nginx または API Gateway。 |
| Image storage | S3 / CloudFront。 |
| Production database | PostgreSQL。 |
| HTTPS / TLS | Nginx reverse proxy。 |
| YOLO model accuracy guarantee | Production data collection と fine-tune が必要。 |
