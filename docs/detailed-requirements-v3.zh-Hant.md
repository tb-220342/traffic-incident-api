# 詳細要件定義書 v3 - Traffic Incident Monitoring API Platform

[返回文檔索引](document-index.zh-Hant.md) | [專案 README](../README.zh-Hant.md)

> [!NOTE]
> v3 是依照目前實作整理的詳細要件定義書。早期 requirement 文件仍保留作為規劃紀錄；若與目前實作不同，以本文件與程式碼為準。

## 1. 專案背景

本系統是交通事件監控平台的後端 API。上游是 AI 影片解析系統，會從高速道路 camera feed 中偵測事件，例如停止車輛、落下物、異常壅塞、逆走或行人進入道路。下游是營運中心 operator 使用的 dashboard，用來快速確認事件並決定是否派遣安全處理隊伍。

核心思想是 **Speed matters**：事件越快送到 operator 面前，越早能採取行動。

## 2. 專案目標

| 目標 | 說明 |
| --- | --- |
| 接收事件 | 提供 API 接收 AI 偵測系統送來的 incident event。 |
| 保存事件 | 將事件持久化到 SQLite，支援 demo 與本機重現。 |
| 查詢事件 | 提供 operator / dashboard 查詢、排序、篩選、分頁。 |
| 即時通知 | 使用 SSE 將新事件與狀態更新推送到 dashboard。 |
| 更新狀態 | 支援 operator 對 incident 進行確認、派遣、解決、回退操作。 |
| 易於重現 | 提供 Docker Compose、seed script、README、Swagger UI。 |
| 可展示 AI 流程 | 提供 YOLO-to-API demo pipeline 與 demo DB 記錄。 |

## 3. 使用者與外部系統

| Actor | 說明 |
| --- | --- |
| AI detection system | 上游系統。偵測道路事件後呼叫 `POST /events`。 |
| Operator | 管制中心工作人員。透過 dashboard 或 API 查詢事件並更新狀態。 |
| Reviewer / interviewer | 面試官。clone repo 後用 Docker Compose 重現 demo。 |
| YOLO demo pipeline | 額外 demo。從影片偵測結果轉成 API event。 |

## 4. Scope

### 4.1 本次範圍內

- FastAPI REST API。
- SQLite persistence。
- SQLAlchemy ORM model。
- Pydantic request / response validation。
- Event list filter、sort、pagination。
- SSE real-time stream。
- Dashboard UI。
- Status update workflow。
- Docker Compose。
- Seed script。
- Pytest。
- YOLO-to-API inference utility。
- 三語 README / docs / dashboard。

### 4.2 本次範圍外

- 正式 production authentication / authorization。
- 多租戶權限管理。
- 高可用 DB cluster。
- cloud deployment pipeline。
- object storage 圖片保存。
- 完整 ML model accuracy guarantee。
- 正式 incident-response runbook。

這些不是忘記做，而是面試課題 scope control。正式上線時會作為 production follow-up。

## 5. 技術選型

| 項目 | 採用 | 理由 |
| --- | --- | --- |
| Web framework | FastAPI | 開發快、Swagger UI 自動生成、Pydantic validation 清楚。 |
| Database | SQLite | 面試 demo 易重現，課題明確允許 SQLite。 |
| ORM | SQLAlchemy 2.x | model / query / repository 分層清楚。 |
| Realtime | SSE | server -> dashboard 單向推送，較 WebSocket 簡潔。 |
| Frontend | Static HTML + Vanilla JS | 不引入重型前端框架，聚焦 API 與即時性展示。 |
| Container | Docker Compose | 面試官可一條指令啟動。 |
| ML demo | YOLO | 展示 AI detector output 寫入 API 的端到端能力。 |

## 6. 功能要件

### F-01 Event Ingestion

| 項目 | 要件 |
| --- | --- |
| Endpoint | `POST /events` |
| 說明 | 接收 AI detection event。 |
| Validation | 使用 Pydantic 驗證必須欄位、enum、confidence 範圍、字串長度。 |
| Persistence | 保存到 `incident_events` table。 |
| Idempotency | 使用 `source_event_id` 防止重複寫入。 |
| Realtime | 新 event 建立後 broadcast `incident.created`。 |

驗收：

- 首次送入 valid payload 回 `201 Created`。
- 相同 `source_event_id` 與相同 payload 回 `200` + `meta.deduplicated=true`。
- 相同 `source_event_id` 但 payload 不同回 `409 Conflict`。
- invalid payload 回 `422 Validation Error`。

### F-02 Event List Query

| 項目 | 要件 |
| --- | --- |
| Endpoint | `GET /events` |
| 說明 | 提供事件列表給 dashboard / operator。 |
| Filter | 支援 severity、event_type、status、camera、source event、highway、time range、delay、confidence。 |
| Sort | 支援 detected_at、ingested_at、updated_at、severity、confidence、detection_delay。 |
| Pagination | `limit` 1-100，`offset` >= 0。 |
| KPI meta | 回傳 total、critical_total、avg_delay_seconds_total、latest_updated_at。 |

### F-03 Event Detail

| 項目 | 要件 |
| --- | --- |
| Endpoint | `GET /events/{incident_id}` |
| 說明 | 查詢單筆 incident。 |
| Not found | 不存在時回 `404`。 |

### F-04 Status Update

| 項目 | 要件 |
| --- | --- |
| Endpoint | `PATCH /events/{incident_id}/status` |
| 說明 | 更新 operator 處理狀態。 |
| Body | `status` 必須，`status_note` optional。 |
| Realtime | 更新後 broadcast `incident.status_updated`。 |
| Noop | 更新到同一 status 時回 `200` + `meta.noop=true`。 |
| Reversible | 允許必要回退，避免誤操作無法修正。 |

狀態轉換：

| From | Allowed To |
| --- | --- |
| `NEW` | `ACKNOWLEDGED`, `RESOLVED` |
| `ACKNOWLEDGED` | `NEW`, `DISPATCHED`, `RESOLVED` |
| `DISPATCHED` | `ACKNOWLEDGED`, `RESOLVED` |
| `RESOLVED` | `ACKNOWLEDGED`, `DISPATCHED` |

### F-05 SSE Stream

| 項目 | 要件 |
| --- | --- |
| Endpoint | `GET /events/stream` |
| Content-Type | `text/event-stream` |
| Event names | `incident.created`, `incident.status_updated` |
| 用途 | 讓 dashboard 即時更新事件與狀態。 |

### F-06 Dashboard

| 項目 | 要件 |
| --- | --- |
| URL | `/ui/` |
| 語言 | English / 日本語 / 繁體中文 |
| KPI | 顯示本頁與總數相關資訊、平均偵測延遲、最新更新時間。 |
| Filter | 明確表現為搜尋 / 篩選，不讓使用者誤解為修改資料。 |
| Pagination | 支援上一頁、下一頁、指定頁數。 |
| Incident card | 顯示 severity、event type、status、camera、detected_at、ingested_at、delay、confidence、source_event_id。 |
| Status action | 可變更狀態，也可回退。 |
| Tooltip / 說明 | 對 label、delay、source id、座標等提供補充說明。 |

### F-07 Seed Script

| 項目 | 要件 |
| --- | --- |
| Command | `python scripts/seed.py` |
| 用途 | 產生 fake events，方便 demo dashboard 與 SSE。 |
| Docker | `docker compose up` 時可啟動 `seed` service。 |

### F-08 Docker Compose

| 項目 | 要件 |
| --- | --- |
| Command | `docker compose up -d --build` |
| Services | `api`, `seed` |
| Port | API 使用 `8000` |
| Persistence | SQLite DB mount 到 `data/` |

### F-09 YOLO-to-API Demo

| 項目 | 要件 |
| --- | --- |
| Script | `python -m yolo.infer_video` |
| Mode | vehicle / damage |
| Output | 可輸出 annotated video，也可 POST event 到 API。 |
| Public repo policy | 不包含 dataset 派生 MP4、snapshot、trained `.pt` weight。 |
| Demo DB | 保留已驗證 YOLO 寫入的 `CAM-YOLO-VIDEO-RDD` records。 |

## 7. API 詳細規格

### 7.1 `POST /events`

Request body：

| Field | Type | Required | Constraint | 說明 |
| --- | --- | --- | --- | --- |
| `source_event_id` | string | yes | 1-128 | 偵測來源 event ID，冪等 key。 |
| `event_type` | enum | yes | see enum | 事件類型。 |
| `severity` | enum | yes | see enum | 重要度。 |
| `description` | string/null | no | max 5000 | 事件描述。 |
| `confidence` | float | yes | 0.0-1.0 | AI 信心分數。 |
| `camera_id` | string | yes | 1-64 | 攝影機 ID。 |
| `highway_id` | string/null | no | max 32 | 高速道路 ID。 |
| `road_marker` | string/null | no | max 64 | 里程標或道路標記。 |
| `lane_no` | string/null | no | max 16 | 車道。 |
| `latitude` | float/null | no | -90 to 90 | 緯度。 |
| `longitude` | float/null | no | -180 to 180 | 經度。 |
| `image_url` | string/null | no | max 500 | snapshot URL。 |
| `detected_at` | datetime | yes | ISO 8601 | AI 偵測時間。 |
| `extra_payload` | object/null | no | JSON | 擴充資訊。 |

### 7.2 `GET /events` query parameters

| Parameter | Type | 說明 |
| --- | --- | --- |
| `severity` | string | 逗號分隔，多選。例：`HIGH,CRITICAL`。 |
| `event_type` | string | 逗號分隔，多選。 |
| `status` | string | 逗號分隔，多選。 |
| `camera_query` | string | 搜尋 camera_id、highway_id、road_marker、lane_no。 |
| `camera_id` | string | camera_id partial match。 |
| `source_event_id` | string | source_event_id partial match。 |
| `highway_id` | string | highway_id partial match。 |
| `detected_from` | datetime | detected_at >= value。 |
| `detected_to` | datetime | detected_at <= value。 |
| `ingested_from` | datetime | ingested_at >= value。 |
| `ingested_to` | datetime | ingested_at <= value。 |
| `min_delay_seconds` | float | detection delay lower bound。 |
| `max_delay_seconds` | float | detection delay upper bound。 |
| `min_confidence` | float | confidence lower bound。 |
| `max_confidence` | float | confidence upper bound。 |
| `sort_by` | enum | `detected_at`, `ingested_at`, `updated_at`, `severity`, `confidence`, `detection_delay`。 |
| `order` | enum | `asc`, `desc`。 |
| `limit` | int | 1-100，預設 20。 |
| `offset` | int | >= 0，預設 0。 |

### 7.3 Enum

| Enum | Values |
| --- | --- |
| `EventType` | `STOPPED_VEHICLE`, `DEBRIS`, `CONGESTION`, `WRONG_WAY`, `PEDESTRIAN`, `UNKNOWN` |
| `Severity` | `LOW`, `MEDIUM`, `HIGH`, `CRITICAL` |
| `Status` | `NEW`, `ACKNOWLEDGED`, `DISPATCHED`, `RESOLVED` |

### 7.4 Response envelope

Single response：

```json
{
  "success": true,
  "data": {},
  "meta": {}
}
```

List response：

```json
{
  "success": true,
  "data": [],
  "meta": {
    "total": 0,
    "limit": 20,
    "offset": 0,
    "critical_total": 0,
    "avg_delay_seconds_total": null,
    "latest_updated_at": null
  }
}
```

Error response：

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request",
    "details": []
  }
}
```

## 8. Data Model

Table：`incident_events`

| Column | Type | Nullable | 說明 |
| --- | --- | --- | --- |
| `id` | string(36) | no | UUID primary key。 |
| `source_event_id` | string(128) | no | unique + index，冪等 key。 |
| `event_type` | enum | no | 事件類型。 |
| `severity` | enum | no | 重要度。 |
| `status` | enum | no | operator workflow 狀態，default `NEW`。 |
| `description` | text | yes | 描述。 |
| `confidence` | float | no | 0-1 信心分數。 |
| `camera_id` | string(64) | no | 攝影機 ID。 |
| `highway_id` | string(32) | yes | 高速道路 ID。 |
| `road_marker` | string(64) | yes | 道路標記。 |
| `lane_no` | string(16) | yes | 車道。 |
| `latitude` | float | yes | 緯度。 |
| `longitude` | float | yes | 經度。 |
| `image_url` | string(500) | yes | snapshot URL。 |
| `detected_at` | datetime | no | AI 偵測時間。 |
| `ingested_at` | datetime | no | API 接收時間。 |
| `status_note` | text | yes | operator 狀態註記。 |
| `extra_payload` | JSON | yes | 擴充資料。 |
| `updated_at` | datetime | no | 最後更新時間。 |

設計重點：

- `detected_at` 與 `ingested_at` 分開，可計算偵測延遲。
- `latitude` / `longitude` optional，因為交通場景常用 camera / road marker / lane 定位。
- `extra_payload` 提供彈性，不必每次 detector 輸出變動都改 schema。
- `source_event_id` unique，可安全處理重送。

## 9. Non-Functional Requirements

| 類別 | 要件 | 目前實現 |
| --- | --- | --- |
| Reproducibility | reviewer 可快速啟動 | Docker Compose + README。 |
| API documentation | 自動 API docs | FastAPI Swagger UI `/docs`。 |
| Validation | request validation | Pydantic。 |
| Persistence | demo 資料保存 | SQLite + Docker volume。 |
| Realtime | 快速通知 operator | SSE。 |
| Testability | 基本 API flow 可測 | pytest，7 tests。 |
| Maintainability | 分層架構 | router / service / repository / schema / model。 |
| Public safety | 不散布大型或授權不明 artifact | `.gitignore` + public release notes。 |

## 10. Acceptance Criteria

| ID | 驗收條件 | 檢查方式 |
| --- | --- | --- |
| AC-01 | API 可啟動 | `docker compose up -d --build` 後 `/health` 回 OK。 |
| AC-02 | 可建立 incident | Swagger `POST /events` 回 `201`。 |
| AC-03 | 可查詢 incident | `GET /events` 回 list + meta。 |
| AC-04 | 可更新 status | `PATCH /events/{id}/status` 回 `200`。 |
| AC-05 | 可即時推送 | Dashboard 或 curl SSE 收到 event。 |
| AC-06 | 可排序 / 篩選 / 分頁 | `GET /events` query parameters 生效。 |
| AC-07 | 可防重複 | 相同 `source_event_id` 重送回 deduplicated。 |
| AC-08 | 可本機重現 | README / deployment guide 可啟動 demo。 |
| AC-09 | 可通過測試 | `pytest -q` 為 `7 passed`。 |
| AC-10 | 可說明取捨 | architecture review notes 會說明 SQLite / SSE / production follow-up。 |

## 11. Production Follow-Up

| 領域 | 改善 |
| --- | --- |
| DB | SQLite -> PostgreSQL，加入 Alembic migration。 |
| Auth | API key / OAuth / JWT，分離 detector 與 operator 權限。 |
| Queue | 高流量時加入 message queue 或 stream。 |
| SSE scale | 多 instance 時加入 Redis / message broker。 |
| Observability | metrics、tracing、structured logs、alerts。 |
| Storage | image_url 對應 object storage，例如 S3。 |
| Security | rate limit、audit log、secret management。 |
| ML Ops | model version、dataset version、inference provenance、false positive/negative monitoring。 |

## 12. 面試說明重點

- 這是面試課題 demo，所以優先做到 end-to-end、可重現、可說明 trade-off。
- API 和 data model 對應 traffic incident workflow。
- SSE 是為了回應 Speed matters。
- SQLite 是降低 reviewer 重現成本，不是 production 最終選擇。
- Production gap 已明確列出，因此不是沒有意識到，而是 scope control。
