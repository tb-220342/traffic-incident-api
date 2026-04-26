# 要件定義書 - 交通事故監控 API 平台

語言: [English](requirements-spec.en.md) | [日本語](requirements-spec.ja.md) | [繁體中文](requirements-spec.zh-Hant.md)

[返回文件索引](document-index.zh-Hant.md) | [專案 README](../README.zh-Hant.md)

> [!NOTE]
> 這是用來對照面試課題範圍與追加要件的整理版規格文件，方便審查目前實作是否滿足交付目標。

原始 PDF: [requirements_spec.md.pdf](requirements_spec.md.pdf)

這是 Back-End Candidate Evaluation 用要件定義書的繁體中文翻譯整理版。

## 01 專案概要

| 項目 | 內容 |
| --- | --- |
| 系統名稱 | Traffic Incident Monitoring API Platform |
| 目的 | 接收 AI 影片解析系統偵測出的事故 / 異常事件，並近即時送達調度中心。 |
| 目標使用者 | 高速道路營運中心工作人員。 |
| 提交形式 | Git repository、README、AI 對話紀錄。 |
| 技術限制 | 無。語言、框架、依賴套件可自由選擇。 |

設計思想是 **Speed matters**。透過 SSE 即時 push，盡量縮短從偵測到畫面顯示的延遲。

## 02 功能要件

### 必做

| ID | Endpoint | 內容 |
| --- | --- | --- |
| F-01 | `POST /events` | 接收 AI 偵測系統送來的事件。使用 Pydantic 驗證 request，保存後立即透過 SSE broadcast。 |
| F-02 | `GET /events` | 取得事件列表。支援 `severity`、`event_type`、`status` filter，`detected_at` / `severity` sort，以及 pagination。 |
| F-03 | `GET /events/{id}` | 取得單一事件。不存在時回 `404`。 |

### 推薦 / Nice To Have

| ID | 功能 | 內容 |
| --- | --- | --- |
| F-04 | `GET /events/stream` | SSE 長連線。每次 `POST /events` 都即時推送到所有 Dashboard，直接回應 "Speed matters"。 |
| F-05 | `PATCH /events/{id}/status` | 更新狀態流程：`NEW -> ACKNOWLEDGED -> DISPATCHED -> RESOLVED`。更新後也要透過 SSE broadcast，讓其他 operator 畫面即時同步。 |
| F-06 | Docker Compose | 用一條 `docker compose up` 啟動整套環境。 |
| F-07 | Seed Script | `python scripts/seed.py` 持續 POST random events。 |
| F-08 | Dashboard UI | 靜態 HTML + vanilla JavaScript。透過 SSE 即時更新。 |
| F-09 | YOLO 整合 | 使用 YOLOv8 解析影片，並把偵測結果自動送到 `POST /events`。這是自選加分項。 |

## 03 API Endpoint 規格

| Method | Path | 用途 | Status |
| --- | --- | --- | --- |
| `POST` | `/events` | 接收事件 | `201 Created` |
| `GET` | `/events` | 取得列表 | `200 OK` |
| `GET` | `/events/{id}` | 取得單筆 | `200 / 404` |
| `PATCH` | `/events/{id}/status` | 更新狀態 | `200 OK` |
| `GET` | `/events/stream` | SSE 長連線 | `200 text/event-stream` |

### Query Parameters - `GET /events`

| Parameter | Type | Example | 說明 |
| --- | --- | --- | --- |
| `severity` | string | `HIGH,CRITICAL` | 可用逗號指定多個值。 |
| `event_type` | string | `DEBRIS` | 單一事件類型。 |
| `status` | string | `NEW` | 單一狀態。 |
| `sort_by` | string | `detected_at` | `detected_at` 或 `severity`。 |
| `order` | string | `desc` | `asc` 或 `desc`，預設 `desc`。 |
| `limit` | int | `20` | 預設 `20`，最大 `100`。 |
| `offset` | int | `0` | 預設 `0`。 |

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

## 04 資料模型

### `incident_events` Table

| Field | Type | 必須 | 說明 |
| --- | --- | --- | --- |
| `id` | UUID | 是 | 主鍵，自動生成。 |
| `event_type` | enum | 是 | `STOPPED_VEHICLE`、`DEBRIS`、`CONGESTION`、`WRONG_WAY`、`PEDESTRIAN`、`UNKNOWN`。 |
| `severity` | enum | 是 | `LOW`、`MEDIUM`、`HIGH`、`CRITICAL`。 |
| `status` | enum | 自動 | `NEW`、`ACKNOWLEDGED`、`DISPATCHED`、`RESOLVED`，預設 `NEW`。 |
| `description` | text | 否 | AI 生成的事件描述。 |
| `confidence` | float | 是 | AI 偵測信心分數，`0.0` 到 `1.0`。 |
| `camera_id` | varchar | 是 | 攝影機 ID。 |
| `highway_id` | varchar | 否 | 路線編號，例如 `E1`、`C2`。 |
| `latitude` | float | 是 | 緯度。 |
| `longitude` | float | 是 | 經度。 |
| `image_url` | varchar | 否 | 偵測當下 snapshot URL。 |
| `detected_at` | timestamp | 是 | AI 偵測端設定的時間。 |
| `ingested_at` | timestamp | 自動 | API 收到事件的時間，用於計算延遲。 |
| `updated_at` | timestamp | 自動 | 最終更新時間。 |

`ingested_at - detected_at` 就是偵測延遲。把它顯示在 Dashboard 可以可視化系統健康度。

## 05 非功能要件

| 項目 | 要件 | 實現方式 |
| --- | --- | --- |
| API 文件 | 自動生成 | FastAPI 內建 Swagger UI，路徑 `/docs`。 |
| Validation | 驗證所有欄位 | Pydantic v2。 |
| Error handling | 明確處理 `400/404/422/500` | FastAPI exception handler。 |
| Environment settings | `.env` 管理 | `python-dotenv`。 |
| Code structure | 分層架構 | `router / service / repository / schema`。 |
| Authentication | Scope 外 | README 明記 production 需要 API key / JWT bearer。 |
| Tests | 主要 endpoint | `pytest` + `httpx`。 |

認證與授權不在本次測試範圍內。README 需要寫明正式環境應使用 API Key 或 JWT Bearer Token。

## 06 YOLO Dataset 選定

| 場景 | 主資料集 | 格式 | 策略 | Fine-tune |
| --- | --- | --- | --- | --- |
| 路肩停車 | BDD100K + MIO-TCD | JSON 轉 YOLO txt | 車輛偵測 + ByteTrack + 路肩 ROI 停留時間規則。 | 必須 |
| 路面碎片 | RAOD (UnicomAI) | mask 轉 bbox | YOLOv8-seg + synthetic copy-paste augmentation。 | 強烈需要 |
| 異常壅塞 | TRANCOS + Mendeley congestion dataset | YOLO txt | 密度計數 + 速度估計 + 閾值規則。 | 必須 |

### Model Selection

| 場景 | Model | Input size | 備註 |
| --- | --- | --- | --- |
| 路肩停車 | `yolov8m.pt` | `640x640` | 與 ByteTrack tracking 併用。 |
| 路面碎片 | `yolov8m-seg.pt` | `1280x1280` | 小目標需要高解析度。 |
| 異常壅塞 | `yolov8s.pt` | `640x640` | 優先速度，重視 counting。 |

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

## 08 實作步驟

### Phase 1 - Backend API，Day 1-2

1. 初始化 project structure 與 dependency list。
2. 定義 SQLAlchemy ORM model、enum、SQLite connection、`Base.metadata.create_all()`。
3. 定義 `IncidentCreate`、`IncidentResponse`、統一 `APIResponse`。
4. 透過 router / service / repository 分層實作 `POST /events`，保存後 SSE broadcast。
5. 實作 `PATCH /events/{id}/status`，並以 `type: "STATUS_UPDATE"` broadcast 狀態更新。
6. 實作 `GET /events` 與 `GET /events/{id}`，支援 filter、sort、pagination、total count。
7. 使用 `asyncio.Queue` 實作 SSE endpoint。
8. 使用 `pytest` 與 `httpx.AsyncClient` 測試主要 endpoint、`422` validation、`404` not found。

### Phase 2 - YOLO Integration，Day 3-4

風險控管：Phase 1 / 3 / 4 全部 100% 完成後再開始。時間不足時可省略 fine-tune，只用 COCO 事前訓練的 `yolov8n.pt` 做 demo。面試官主要評價 end-to-end 系統整合能力，不是模型精度。

Minimum demo:

1. 用 `yolov8n.pt` 解析任意高速道路影片。
2. 偵測到 `car` 後，以 `STOPPED_VEHICLE` event POST。
3. 即使 fine-tune 未完成，只要 API 端到端連通就足夠。

時間允許時:

1. 路面碎片：把 RAOD mask 轉 bbox，fine-tune YOLOv8 segmentation。
2. 路肩停車：用 BDD100K / MIO-TCD fine-tune，ByteTrack tracking，定義 shoulder ROI，停留 N 秒後發事件。
3. 異常壅塞：用 TRANCOS / Mendeley 訓練 vehicle counter，計算 ROI density 與 average speed，超過閾值時發 `CONGESTION`。
4. 把所有 detection 整合到 `POST /events`。

### Phase 3 - Infrastructure，Day 4

1. 新增基於 `python:3.11-slim` 的 Dockerfile。
2. 新增包含 API service 與 persistent SQLite volume 的 `docker-compose.yml`。
3. 新增 seed script，每 2-5 秒以日本高速道路附近座標 random 生成 3 種 event。

### Phase 4 - Dashboard UI，Day 5

1. 建立 static HTML dashboard，包含 `severity`、`event_type`、`status` filters。
2. event card 顯示 `detected_at`、`severity`、location、description。
3. 依 severity 做 color coding。
4. 使用 rendered ID 的 `Set`，避免初始 load 與 SSE push race condition 造成重複顯示。
5. 收到 `STATUS_UPDATE` 時只更新既有 card，不新增 card。
6. 每個 event 顯示 `ingested_at - detected_at` 的 detection delay。

## 09 Scope 外

| 項目 | Production approach |
| --- | --- |
| Authentication / Authorization | API Key 或 JWT Bearer。 |
| Rate limiting | Nginx 或 API Gateway。 |
| Image storage | S3 / CloudFront。 |
| Production database | PostgreSQL。 |
| HTTPS / TLS | Nginx reverse proxy。 |
| YOLO model accuracy guarantee | 需要 production data collection 與 fine-tune。 |
