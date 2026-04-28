# 面試用講稿

[返回文檔索引](document-index.zh-Hant.md) | [架構審查備忘](architecture-review-notes.zh-Hant.md)

> [!NOTE]
> 這份稿子以「日文可直接講」為主，搭配中文提示。可以依面試時間縮短或展開。

## 1. 30 秒開場

### 日本語稿

本日はお時間いただきありがとうございます。  
今回の課題では、交通インシデント監視プラットフォームのバックエンドとして、AI 動画解析システムから検知イベントを受け取り、管制センターの operator が素早く確認・対応できる API を実装しました。

主な機能は、`POST /events` によるイベント受信、`GET /events` による検索・filter・pagination、`PATCH /events/{id}/status` による対応状況更新、そして SSE による dashboard へのリアルタイム通知です。  
Docker Compose で一括起動でき、Swagger UI と簡易 dashboard で動作確認できます。

### 中文提示

重點：

- 先說這是交通事件監控後端。
- 強調 API、查詢、狀態更新、SSE。
- 說可以 Docker Compose 重現。

## 2. 1 分鐘專案概要

### 日本語稿

このシステムの想定フローは、まず AI detection system が停止車両、落下物、渋滞、逆走などを検知します。  
その結果を API が受信し、SQLite に保存します。  
operator は dashboard または API から event を検索し、severity、event type、status、camera、時間範囲などで filter できます。

また、課題文に “Speed matters” とあったため、単純な polling ではなく Server-Sent Events を使いました。新規 event の作成や status 更新が起きたら、dashboard に push されます。

### 中文提示

要把資料流講清楚：

```text
AI detector -> POST /events -> DB -> GET /events / Dashboard -> operator action
```

## 3. API 設計說明

### 日本語稿

API は incident lifecycle に合わせて設計しました。

`POST /events` は検知システムからの入力点です。  
`GET /events` は operator が一覧を確認するための endpoint で、sort、filter、pagination に対応しています。  
`GET /events/{id}` は詳細確認用です。  
`PATCH /events/{id}/status` は operator の対応状況を更新するためです。  
`GET /events/stream` は dashboard 向けの SSE stream です。

特に `source_event_id` を idempotency key として使っています。検知システム側で retry が起きる可能性があるので、同じ event が再送されても二重登録しないようにしています。同じ payload なら deduplicated、内容が違えば conflict として扱います。

### 中文提示

面試官問 API 設計時，重點回答：

- endpoint 和事件生命週期一致。
- `source_event_id` 是很重要的設計。
- 查詢 endpoint 支援 operator 實際工作需求。

## 4. Data Model 說明

### 日本語稿

Data model は、operator が判断するために必要な情報を中心に設計しました。  
event type、severity、status、description、camera id、location、confidence、detected_at、ingested_at などを持っています。

`detected_at` と `ingested_at` を分けた点が重要です。  
これにより、AI が検知した時刻と API が受信した時刻の差を計算でき、detection delay を dashboard に表示できます。これは system health の確認にも役立ちます。

また latitude / longitude は optional にしました。交通システムでは GPS より camera id、road marker、lane number で位置を表現する場合もあるためです。

### 中文提示

必講：

- `detected_at` vs `ingested_at`。
- `confidence` 讓 operator 知道 AI 判斷可靠度。
- `latitude/longitude` optional 是合理設計，不是缺漏。

## 5. SSE 即時通知

### 日本語稿

リアルタイム通知には SSE を使いました。  
理由は、今回の要件では主に server から dashboard への一方向通知だからです。WebSocket も選択肢ですが、双方向 communication が必要な場面ではないため、SSE の方が実装も運用も軽く、課題に合っていると判断しました。

Polling の場合は、どうしても遅延が出たり、無駄な request が増えたりします。SSE であれば、event を受信した直後、または status が更新された直後に dashboard へ push できます。

### 中文提示

如果問「為什麼不用 WebSocket」：

```text
今回の要件は双方向通信ではなく、server から dashboard への一方向通知が中心なので、SSE の方が simple で十分です。
```

## 6. SQLite 採用理由

### 日本語稿

SQLite は今回の interview / demo 用の選択です。課題文でも “even SQLite is perfectly fine” とあり、reviewer が clone 後すぐに動かせることを優先しました。

Docker Compose では SQLite file を volume mount しているので、demo data も保持できます。  
ただし production で高頻度 write や複数 instance を考える場合は、PostgreSQL に移行すべきです。この点は README と architecture notes にも production follow-up として明記しています。

### 中文提示

這裡要小心，不要說 SQLite 適合正式環境。要說：

- Demo / assignment 合理。
- Production 會換 PostgreSQL。
- 這是 trade-off。

## 7. Dashboard 說明

### 日本語稿

Dashboard は front-end の評価対象ではないと課題文にありましたが、API の動作を見せるために実装しました。  
三言語切り替え、filter、pagination、KPI、status 更新、tooltip を入れています。

Filter は検索専用で、既存データを変更するものではないことが分かるようにしました。  
また status は一方向だけでなく、誤操作時に戻せるようにしています。

### 中文提示

Dashboard 是 demo 補強，不是主戰場。講：

- 用來展示 API + SSE。
- 三語化是加分。
- UI 修過避免 filter 被誤解成資料修改。

## 8. YOLO 說明

### 日本語稿

YOLO integration は必須要件ではありませんが、AI detection system から API へ event を送る流れをより具体的に見せるために追加しました。

`yolo.infer_video` で動画を解析し、検出結果を `POST /events` に送ることができます。  
ただし public repository には dataset 由来の動画、snapshot、trained `.pt` weight は含めていません。ライセンスと再配布リスクを考慮し、script と training summary、demo DB の検証済み record のみを含めています。

### 中文提示

如果問 YOLO：

- 選作，但做了 end-to-end。
- public repo 不放 dataset 派生影片/權重是合規考量。
- DB 裡只有特定 `CAM-YOLO-VIDEO-RDD` 兩筆是真 YOLO 寫入，其餘多數是 seed/demo。

## 9. Production Follow-Up

### 日本語稿

Production 化する場合、まず SQLite を PostgreSQL に置き換え、Alembic migration を入れます。  
次に authentication / authorization を追加し、detection system と operator の権限を分離します。  
また、traffic が増えた場合は ingestion の前段に queue や stream を置き、multi-instance で SSE broadcast するために Redis や message broker を使います。

Observability も重要です。ingestion latency、SSE connection、error rate、false positive / false negative などを metrics と alert で監視する必要があります。

### 中文提示

Production 改善固定回答：

- PostgreSQL + Alembic。
- Auth / authorization。
- Queue / stream。
- Redis/message broker for SSE scale。
- Metrics/tracing/logging/alert。
- Backup / retention / deployment pipeline。

## 10. Demo 流程稿

### 日本語稿

まず Docker Compose で起動します。

```powershell
docker compose up -d --build
```

次に Swagger UI を開きます。

```text
http://127.0.0.1:8000/docs
```

ここで `POST /events` を実行して event を作成します。  
その後 `GET /events` で filter、sort、pagination を確認します。  
次に `PATCH /events/{id}/status` で status を `ACKNOWLEDGED` に変更し、dashboard 側に反映されることを見せます。

Dashboard は以下です。

```text
http://127.0.0.1:8000/ui/
```

ここで新しい incident card、KPI、filter、pagination、status 更新を確認できます。

### 中文提示

實際 demo 順序：

1. Docker 啟動。
2. `/docs` 建立事件。
3. `/events` 查詢。
4. `/ui/` 看 dashboard。
5. PATCH status。
6. 說 SSE 會即時反映。

## 11. 常見提問與回答

### Q1. なぜ FastAPI ですか？

FastAPI は Pydantic validation と Swagger UI が標準で使いやすく、今回のように API contract を明確に見せたい課題に合っています。また async endpoint も書きやすく、SSE との相性も良いです。

### Q2. なぜ SQLite ですか？

課題文で SQLite でも良いとされており、reviewer が簡単に clone して動かせることを優先しました。production では PostgreSQL に移行する前提です。

### Q3. なぜ SSE ですか？

operator dashboard への一方向 push が中心なので、WebSocket より軽く、polling より遅延が少ないためです。

### Q4. Data model で一番意識した点は？

`detected_at` と `ingested_at` を分けた点です。これにより detection delay を計算でき、speed matters という課題文に対して具体的な指標を出せます。

### Q5. 認証がないのは問題では？

今回の課題 scope では API/schema/design と動作確認を優先しました。本番化では API key、OAuth、JWT、operator 権限管理を追加します。

### Q6. YOLO の精度は保証できますか？

この提出では YOLO は optional demo integration です。精度保証には production data collection、annotation、evaluation、model versioning、false positive / false negative monitoring が必要です。

### Q7. 一番工夫した点は？

API だけでなく、operator workflow と speed requirement を意識して、status update、SSE、dashboard、detection delay、idempotency を入れた点です。

### Q8. 一番の trade-off は？

SQLite と簡易 dashboard です。面接課題としては再現性と説明しやすさを優先し、本番運用に必要な PostgreSQL、auth、observability は production follow-up として明示しました。

## 12. 3 分版まとめ

### 日本語稿

今回の実装では、AI detection system と operator dashboard の間に入る back-end layer を作りました。  
`POST /events` で検知 event を受け取り、SQLite に保存し、`GET /events` で検索・filter・pagination できるようにしています。  
operator の対応状況は `PATCH /events/{id}/status` で更新でき、更新内容は SSE で dashboard に即時 push されます。

設計上は、`source_event_id` による idempotency、`detected_at` と `ingested_at` の分離、confidence と severity の保持を重視しました。  
これにより、重複送信、検知遅延、優先度判断に対応できます。

SQLite は demo と review の再現性を優先した選択で、本番では PostgreSQL、auth、queue、observability、backup を追加する想定です。  
また optional として YOLO-to-API pipeline も用意し、AI 検知結果が API に入る end-to-end flow を確認できるようにしました。

## 13. 30 秒版まとめ

### 日本語稿

この課題では、AI 動画解析システムから traffic incident event を受け取り、operator が素早く確認・対応できる FastAPI backend を作りました。  
API 設計、data model、SSE による realtime push、SQLite による簡単な再現性、Docker Compose、dashboard、test、AI 利用ログまで含めています。  
本番化では PostgreSQL、auth、queue、observability を追加する方針です。

## 14. 面試前最後檢查

- GitHub repo 是 public。
- README 打開後可找到 Architecture Review Notes。
- Docker Compose 可以啟動。
- Swagger UI 可以跑 `POST /events`、`GET /events`、`PATCH /events/{id}/status`。
- Dashboard 可以開。
- 可以說明 SQLite 只是 demo trade-off。
- 可以說明 SSE vs WebSocket。
- 可以說明 `detected_at` / `ingested_at`。
- 可以說明 production follow-up。
