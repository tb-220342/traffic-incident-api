# 架構審查備忘

語言: [English](architecture-review-notes.md) | [日本語](architecture-review-notes.ja.md) | [繁體中文](architecture-review-notes.zh-Hant.md)

[返回文檔索引](document-index.zh-Hant.md) | [專案 README](../README.zh-Hant.md)

> [!NOTE]
> 這份文件集中對應後端面試課題常看的評價點：API 設計、schema / data model、即時通知、技術取捨，以及本番化改善方向。

## 1. API 設計

API 依照課題場景中的 event lifecycle 設計：偵測系統產生 incident，operator 查詢 incident，並更新處理狀態。

| Endpoint | 設計理由 |
| --- | --- |
| `POST /events` | 接收 AI / 影片解析側送來的偵測 event。使用 Pydantic 驗證輸入，並保存已接受的 event。 |
| `GET /events` | 提供 operator 使用的事件列表。filter、sort、pagination 支援管制中心搜尋與 triage。 |
| `GET /events/{id}` | 查詢單筆 incident 詳細。 |
| `PATCH /events/{id}/status` | 讓 operator 更新確認、處理、解決狀態。為了處理誤操作，也允許必要時把 status 往回調整。 |
| `GET /events/stream` | 將新 event 與 status 更新 stream 給 dashboard client。 |

`source_event_id` 作為 idempotency key。偵測系統或 retry 流程可能重送同一筆 event，因此相同 `source_event_id` 且 payload 相同時視為安全重複；若內容衝突則回 `409 Conflict`。

## 2. 資料模型

資料模型刻意保持精簡，但保留 operator 判斷所需資訊：發生什麼事、在哪裡、優先度多高、偵測可信度如何。

| 欄位群 | 設計理由 |
| --- | --- |
| 識別資訊 | `id` 是內部 UUID。`source_event_id` 用於對應偵測來源與冪等處理。 |
| 事件類型 | `event_type` 表示停止車輛、落下物、壅塞、逆走、行人偵測等類別。 |
| 優先度 | `severity` 讓 operator 優先處理重大 event。 |
| Operator workflow | `status`、`status_note`、`updated_at` 支援處理流程與操作追蹤。 |
| 時間 | 分開 `detected_at` 與 `ingested_at`，可計算從偵測到 API 接收的延遲。 |
| 位置 | `camera_id`、`highway_id`、`road_marker`、`lane_no`、緯度經度支援人工確認與未來地圖整合。 |
| 證據與補充 | `description`、`image_url`、`extra_payload` 保存 context，避免 schema 太早過度固定。 |
| ML 信心分數 | `confidence` 讓低信心 event 可以被更謹慎地審查。 |

緯度與經度是 optional，因為交通系統有時會用 camera、road marker、lane 來定位 incident，而不是一定依賴 GPS。

## 3. 即時通知方式

課題寫明「Speed matters」。operator 越早看到 incident，就能越早採取行動。因此本實作採用 Server-Sent Events (SSE)。

SSE 適合這個場景，因為主要即時流程是單向：server 推送到 dashboard。dashboard 需要收到 `incident.created` 與 `incident.status_updated`，但不需要完整雙向 WebSocket channel。

不用 polling 的理由:

- polling 容易產生延遲，也會增加無意義的重複 request。
- SSE 可以在 API 接收或更新 event 後立即 push。
- SSE 在 demo 環境容易啟動，也方便用 browser 或 terminal 檢查。

不用 WebSocket 的理由:

- WebSocket 適合複雜雙向互動。
- 本課題主要需要 server 到 dashboard 的單向營運通知。
- SSE 讓架構更小，同時能回應 speed requirement。

## 4. SQLite 採用理由

SQLite 是面試課題 / demo 用的務實選擇，不是說它最適合正式交通監控系統。

這裡使用 SQLite 合理的原因:

- 課題明確寫到「even SQLite is perfectly fine」。
- reviewer 不需要準備 DB server，clone 後即可啟動。
- Docker Compose 可透過 volume mount 持久化 SQLite file。
- repository layer 已分離，未來換 PostgreSQL 時可盡量維持 public API contract。

SQLite 的取捨也很清楚：它不適合高寫入、多 instance 的正式部署。這點已作為 production follow-up 記載，而不是隱藏風險。

## 5. 本番化改善點

若要正式上線，建議補上以下內容。

| 領域 | 改善內容 |
| --- | --- |
| Database | 將 SQLite 換成 PostgreSQL，並加入 Alembic migration。 |
| Reliability | detector traffic 增加時，在 event ingestion 前加入 queue / stream。 |
| Authentication | 為偵測系統與 operator 加入 API key、OAuth 或 service-to-service auth。 |
| Authorization | 分離 detector 寫入權限與 operator 閱讀 / 更新權限。 |
| Observability | 加入 metrics、tracing、structured logs、ingestion latency / SSE failure alert。 |
| Scalability | 多 instance SSE broadcast 可使用 Redis、PostgreSQL LISTEN/NOTIFY 或 message broker。 |
| Operations | 補上 backup、retention policy、deployment pipeline、incident-response runbook。 |
| ML integration | 管理 model / dataset version，保存 inference provenance，監控 false positive / false negative。 |

## 總結

目前 architecture 是為面試課題刻意控制範圍：小、容易啟動、能 end-to-end 展示。API 與 data model 對應 traffic incident workflow，SSE 回應 speed requirement，SQLite 降低 reviewer 重現成本，而 production gap 也被明確列出，方便說明 scope control 與 trade-off。
