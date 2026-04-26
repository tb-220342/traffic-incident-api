# AI 對話來源 - 繁體中文翻譯版

語言: [English](ai-conversation-source.en.md) | [日本語](ai-conversation-source.ja.md) | [繁體中文](ai-conversation-source.zh-Hant.md)

[返回文件索引](document-index.zh-Hant.md) | [AI 使用紀錄](ai-log.zh-Hant.md)

> [!NOTE]
> 這是 AI 對話證據的易讀翻譯版。為了保留可追溯性，原始抽出文字也以獨立文件保存。

原始 PDF: [Claude_geminiconversation.md.pdf](Claude_geminiconversation.md.pdf)  
Raw 抽出來源: [ai-conversation-source.md](ai-conversation-source.md)

這份文件是 raw AI conversation record 的繁體中文翻譯整理版。必要的 code fragment 與技術 keyword 會保留原文，以方便面試官對照。

## Q1. 初步想法：會如何完成這個課題

Claude 建議使用 **FastAPI + SQLite + SQLAlchemy**。理由是 Pydantic schema validation 容易寫得乾淨，async 對後續 real-time delivery 友善，SQLite 輕量且本機不需要重型 DB。

Schema 設計重點是分開 `detected_at` 與 `ingested_at`，以便追蹤偵測延遲。候選欄位包含 `id`、`event_type`、`severity`、`description`、`camera_id`、`highway_id`、`latitude`、`longitude`、`image_url`、`confidence`、`status`、`detected_at`、`ingested_at`。

針對 "Speed matters"，Claude 建議不要只做 polling，而是實作 **SSE (Server-Sent Events)**。對後端到 Dashboard 的單向推送而言，SSE 比 WebSocket 更輕，也很適合「新事件自動顯示」。

建議實作順序:

1. `POST /events`，包含 schema validation。
2. `GET /events`，包含 filter 與 sort。
3. SSE real-time stream。
4. Docker Compose。
5. 定期 POST fake event 的 seed script。
6. 簡單 HTML UI，不需要先做 React。

認證與授權被視為 scope 外，但 README 應寫明 production 會加入 API key / JWT。

## Q2. YOLO 要用哪些資料集訓練

Claude 先澄清：YOLO training 並不是這份 backend assignment 的必須內容。課題假設上游 AI video-analysis system 已經能偵測事件；提交重點是 API layer：接收偵測結果並傳給調度員。

核心 contract 是:

```text
POST /events        -> 接收 detector output
GET /events/stream  -> 透過 SSE broadcast 到 dashboard
```

## Q3. 我自己也想試試偵測

Claude 認為這可以作為 full-stack extension，但 dataset 要看實際偵測目標。

候選 dataset:

- 通用車輛偵測: COCO、VisDrone。
- 高速公路 / 事故場景: CADP、D2-City、BDD100K、DETRAC。
- 路面 debris: 公開 dataset 稀少，常需要自標或合成資料。

不同 incident category 的本質不同:

- 路肩停車: vehicle detection + tracking + location rule。
- 逆行: tracking 與 direction analysis。
- 路面障礙物 / debris: object detection 或 segmentation。
- 壅塞: tracking 與 counting，不只是單張圖片偵測。

Claude 提醒，評分重點主要是 backend quality，不是 detector training，所以 YOLO 不應占用 API 實作時間。

## Q4. 兩邊都做

Claude 建議拆成兩條線:

- Main track: 先完成面試課題 API，使用 FastAPI、SQLite、SSE。
- Side track: 用 Ultralytics YOLOv8 做整合。

YOLO script 可以直接扮演 "AI detection system"，向自己的 API 發 `POST /events`。

```text
camera / video file
-> YOLO detection script
-> 偵測到異常
-> POST /events
-> FastAPI backend
-> SSE push
-> dispatch dashboard
```

建議順序:

1. 先 2-3 天完成 API。
2. 再 1-2 天接 YOLO。
3. 最後在 README 寫清楚整條鏈路。

## Q5. 文件要求完成什麼、資料集用什麼、技術棧用什麼

Claude 總結課題要求:

- 核心: `POST` endpoint 接收 AI detection events。
- 核心: `GET` endpoint 給前端查詢，支援 filter / sort。
- 加分: Docker Compose、database、simple UI、fake event generator。
- 提交物: Git repository、README、AI tool conversation log。

文件沒有指定 dataset，因為題目假設 detector 已存在。YOLO 是自選加戲；BDD100K 是合理候選，但不是考核點。

建議技術棧:

- Backend: FastAPI。
- Database: SQLite + SQLAlchemy。
- Real-time push: SSE。
- Container: Docker Compose。
- UI: plain HTML + JavaScript。
- Optional detector: YOLOv8。

## Q6. 提交前如何保障品質

Claude 給出的 checklist:

- Directory structure 清楚，不要所有東西塞同一個 file。
- 完整處理 `400`、`404`、`422`、`500`。
- 嚴格使用 Pydantic validation。
- 用 repository pattern 隔離 database access。
- Swagger docs 要清楚。
- filter / sort 要有合理 default 與 boundary handling。
- response wrapper 要統一。
- `docker compose up` 一條命令能跑起來。
- seed script 讓 reviewer 立刻看到資料。
- README 讓 reviewer 不需要猜。
- SSE、confidence、`detected_at` vs `ingested_at` 這些細節能展現業務理解。

## Q7. Directory structure 與 database schema

Claude 提議的 structure:

```text
traffic-incident-api/
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models/incident.py
│   ├── schemas/incident.py
│   ├── routers/incidents.py
│   ├── routers/stream.py
│   ├── services/incident_service.py
│   ├── services/sse_manager.py
│   └── core/config.py
├── scripts/seed.py
├── yolo/detector.py
├── ui/index.html
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

Database model 使用 UUID primary key，event type / severity / status enum，可選 description / image field，confidence，camera/location，並分開 detection 與 ingestion timestamp。

## Q8. 畫架構圖並整理詳細要件定義書

Claude 把內容整理成 `requirements_spec.md`，包含:

1. 專案概要。
2. 功能要件。
3. API 端點規格。
4. 資料模型。
5. 非功能要件。
6. YOLO 資料集選擇。
7. 目錄結構。
8. 實作階段。
9. 範圍外。

## Q9. 資料呢

Claude 推薦 BDD100K 作為主要 driving-scene dataset，因為它有大量行車影片，以及 car / truck / pedestrian / motorcycle / traffic light / traffic sign 等 label。

補充 dataset:

- VisDrone: dense vehicle scene。
- COCO: pretrained vehicle / person category。
- DETRAC: vehicle detection + tracking。

但 BDD100K 沒有直接標註 road debris 或 shoulder-stopped vehicle，因此仍需要 fine-tune 與 rule。

## Q10. 文件中提到的偵測場景都要有

Claude 整理出三個 scenario:

1. Vehicle stopped on the shoulder。
2. Debris on the road。
3. Abnormal congestion。

實作方向:

- Stopped vehicle: 偵測車輛、追蹤速度，判斷是否停在 shoulder ROI。
- Road debris: 公開 dataset 少，通常需要 custom / synthetic dataset。
- Congestion: density + speed analysis。

Claude 建議誠實處理：用 pretrained YOLO 做 vehicle/person detection，對 stopped vehicle 與 congestion 加 rule；debris 則在 README 寫明需要 domain-specific data。比假裝三者都已訓練成熟更可信。

## Q11. 找 dataset 的提示詞

Claude 產生了尋找 dataset 用的 prompt，目標是:

1. Stopped vehicle on highway shoulder。
2. Road debris / foreign objects。
3. Abnormal traffic congestion。

Prompt 要求回覆 download link、annotation format、是否需要 fine-tune、dataset limitations，以及 synthetic data / rule-based fallback。

## Q12. Dataset 搜尋結果整理

| Scenario | Main dataset | Format | Fine-tune | Notes |
| --- | --- | --- | --- | --- |
| 路肩停車 | BDD100K + MIO-TCD | JSON to YOLO txt | 必須 | detection 不夠，還要 tracking、ROI、dwell time。 |
| Road debris | RAOD | segmentation mask | 必須 + augmentation | 最對口，建議 YOLOv8-seg。 |
| 異常壅塞 | TRANCOS + Mendeley congestion dataset | YOLO txt | 必須 | counting + speed + density analysis。 |

三個場景的本質:

- Debris: 比較接近單幀 detection。
- Shoulder stop: detection + tracking + time threshold。
- Congestion: detection + counting + density/speed reasoning。

## Q13-Q14. 具體要件定義書與 Markdown 版本

Claude 產生了 Markdown 版要件與實作步驟。結構為:

```text
01 概要
02 功能要件
03 API 規格
04 資料模型
05 非功能要件
06 資料集選擇
07 目錄結構
08 實作步驟，階段 1-4
09 範圍外
```

## Q15-Q16. Feedback 與更新

收到 review feedback 後，Claude 整合了三個重點:

1. YOLO time-sink risk: backend、infrastructure、UI 完成後再開始 YOLO，fine-tune 可選。
2. `PATCH /events/{id}/status` 也必須 SSE broadcast。
3. Frontend deduplication: 使用 rendered ID 的 `Set`，並分開處理 `STATUS_UPDATE` 與 new event。

更新後的 plan 重點是 end-to-end integration，而不是 model accuracy。

```text
yolov8n.pt + highway video
-> detect car
-> POST /events as STOPPED_VEHICLE
-> dashboard updates through SSE
```

## Q17. Codex 完成後如何展示給面試官

Claude 建議 demo-first:

1. 先打開 Dashboard，讓面試官看到結果在跑。
2. 跑 seed script，展示 incident real-time 出現。
3. 打開 `/docs`，展示 Swagger API design 與 filter/sort parameter。
4. 手動 `POST` 一個 CRITICAL event，展示 Dashboard 即時更新。
5. `PATCH` status，展示狀態 real-time sync。
6. 如果有 YOLO，播放 video demo，讓它自動觸發 API event。

應主動說明的 trade-off:

- SSE 而不是 WebSocket：單向 push 足夠，實作更簡單。
- SQLite 而不是 PostgreSQL：課題允許 SQLite，local demo 可重現性更重要。
- YOLO fine-tune：這是 backend evaluation，所以優先展示 end-to-end demo 與設計說明。

## Gemini Review Summary

Gemini 以 candidate evaluation document 與 requirements spec 做 review。

優點:

- SSE 直接回應 "Speed matters"。
- `detected_at` vs `ingested_at` 展現 observability 思維。
- Router / Service / Repository 分層標準且易維護。
- Docker、database、UI、seed script 覆蓋 nice-to-have scope。
- YOLO integration 展現 AI system context 的 end-to-end 連接。

風險與調整:

- 避免 YOLO time sink，core API 完成後再做。
- status update 後也要 broadcast。
- 加 frontend deduplication 避免重複 card。

總評：更新後的 document 已達 Technical Design Document 水準，可以直接交給 development team 實作。
