# 実装状況 vs 要件 v2

言語: [English](implementation-vs-requirements-v2.en.md) | [日本語](implementation-vs-requirements-v2.ja.md) | [繁體中文](implementation-vs-requirements-v2.md)

最終更新: 2026-04-26 (Asia/Tokyo)

## 検証スナップショット

- `pytest`: `7 passed`
- `docker compose up -d --build`: 検証済み
- Docker `/health`: `200 OK`
- `POST /events`:
  - 初回作成: `201 Created`
  - 同じ `source_event_id` かつ同じ payload: `200 OK` + `meta.deduplicated=true`
  - 同じ `source_event_id` で内容が衝突: `409 Conflict`
- `GET /events/stream`: `200 text/event-stream`
- Dashboard:
  - `/ui/` は `200` を返す
  - front-end が `/events` を呼び出す
  - SSE が `/events/stream` に接続する
  - English / 日本語 / 中文 の切り替えに対応

## 完成度チェックリスト

### P0 必須範囲

| 項目 | 状態 | 説明 |
| --- | --- | --- |
| `POST /events` 受信 API | 完了 | validation、冪等性、`source_event_id` dedup、`201/200/409` をサポート |
| `GET /events` 一覧 API | 完了 | `severity`、`event_type`、`status`、`camera_id`、`highway_id`、sort、pagination をサポート |
| `GET /events/{id}` 詳細 API | 完了 | `404 NOT_FOUND` をサポート |
| `PATCH /events/{id}/status` | 完了 | 許可されたワークフロー遷移、誤操作時の戻し操作、no-op、未対応ジャンプ時の `409 INVALID_STATUS_TRANSITION` を実装 |
| `GET /events/stream` SSE | 完了 | `incident.created`、`incident.status_updated`、keep-alive を送信 |
| SQLite 永続化 | 完了 | ローカルと Docker の両方で SQLite を使用 |
| 統一レスポンス形式 | 完了 | `success/data/meta` と `success/error` を使用 |
| UTC 時刻 | 完了 | `detected_at`、`ingested_at`、`updated_at` を UTC + `Z` で出力 |
| 基本ログ | 完了 | request、SSE 接続、event 作成、dedup、status 更新を記録 |
| README と AI log | 完了 | README と AI 利用ログを含む |

### P1 Demo 加点要素

| 項目 | 状態 | 説明 |
| --- | --- | --- |
| Docker 一括起動 | 完了 | `api` と `seed` を Docker Compose で起動可能 |
| fake event generator | 完了 | `scripts/seed.py` が valid event を継続送信 |
| Dashboard | 完了 | 検索結果、詳細、delay、戻せる status action、SSE 更新を表示 |
| Dashboard 三言語切り替え | 完了 | English / 日本語 / 中文 に対応 |
| Dashboard usability 改善 | 完了 | 検索専用 Filter 説明、ページ直接指定、1ページ件数、イベントタイトル多言語化、enum dropdown、手入力 / 範囲検索、項目 tooltip、ステータス変更前確認を追加 |
| KPI / Detection delay 表示 | 完了 | 表示件数、重大件数、平均遅延を「このページ / 該当総数」で表示し、検索時刻と DB 更新時刻も表示 |

### P2 YOLO / 動画連携

| 項目 | 状態 | 説明 |
| --- | --- | --- |
| `infer_video.py` から API 送信 | 完了 | 2026-04-26 に `rdd_damage_short.mp4` で確認済み。`CAM-YOLO-VIDEO-RDD` から `DEBRIS` event が 2 件保存された |
| 学習済み weight の local 保持 | 完了 | MIO、RDD2022、TRANCOS の run は `<DATA_ROOT>\runs` に保持。public repo には `.pt` weight は含めず、`model-artifacts/` には training summary のみを置く |
| ML asset を repository 外に配置 | 完了 | dataset、cache、run、snapshot は `../traffic-incident-data` が default。`TRAFFIC_DATASETS_ROOT` で変更可能 |
| 動画品質確認 | demo 可能 / 手動確認 | 短い確認用動画と YOLO box 出力は `<DATA_ROOT>\yolovideotest` に local 保持。public repo では dataset 由来 MP4/snapshot を除外し、確認済み API event は demo DB に残す |

## 手動で確認すべき点

- `http://127.0.0.1:8000/ui/` を開き、Dashboard の見た目を確認する。
- `EN / 日本語 / 中文` を切り替え、ラベル、インシデントタイトル、event tag、status button が変わることを確認する。
- Filter 領域が検索専用に見え、新規登録やデータ変更の入力欄に見えないことを確認する。
- 上部 KPI が絞り込み条件に連動し、「このページ / 該当総数」で出ることを確認する。
- 最終 KPI に検索時刻と DB 更新時刻が表示されることを確認する。
- 1ページ件数を変え、ページ番号を入力し、移動 / 前へ / 次へを押して、表示範囲とカードが更新されることを確認する。
- カメラ / 位置、Camera ID、Source Event ID、検知 / 受信時刻、遅延秒数、信頼度の詳細検索を試す。
- label や項目名に hover し、重要度、イベント種別、ステータス、検知遅延、位置、座標、Source ID、Camera ID の説明を確認する。
- Dashboard の status button を押し、前後どちらにも変更できることを確認する。
- YOLO を demo に含める場合は、実際の道路動画で false positive / false negative を見る。
- GitHub に push する前に、raw/prepared 画像、MP4、snapshot、`.pt` weight、cache、secret、中間 epoch checkpoint が stage されていないことを確認する。

## 実行方法

### Docker

```powershell
cd <repo-root>
docker compose up -d --build
docker compose ps
```

開く場所:

- Swagger: `http://127.0.0.1:8000/docs`
- Dashboard: `http://127.0.0.1:8000/ui/`

seed を止める:

```powershell
docker compose stop seed
```

停止:

```powershell
docker compose down
```

### ローカル API

```powershell
cd <repo-root>
.\.venv\Scripts\uvicorn app.main:app --reload
```

### テスト

```powershell
cd <repo-root>
.\.venv\Scripts\pytest
```

## 手動 API 確認

Swagger または API client から以下を送信:

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

期待結果:

- `201 Created`
- optional coordinates は `null`
- `meta.deduplicated = false`
- `detected_at` は UTC に正規化される。例: `2026-04-23T01:00:00Z`

dedup 確認:

- 同じ body をもう一度送る
- `200 OK`、`meta.deduplicated=true`、同じ `id` を期待

conflict 確認:

- 同じ `source_event_id` のまま `severity` などを変更
- `409 DUPLICATE_CONFLICT` を期待

SSE 確認:

```powershell
curl.exe -N http://127.0.0.1:8000/events/stream
```

期待される event:

- `incident.created`
- `incident.status_updated`

## YOLO 確認

車両 / 停止車両 / 渋滞:

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode vehicle `
  --weights <DATA_ROOT>\runs\mio-localization\mio-stage2-20260421-234643\weights\best.pt `
  --source <path-to-highway-video>.mp4 `
  --base-url http://127.0.0.1:8000
```

路面異常 / debris:

```powershell
cd <repo-root>
.\.venv\Scripts\python.exe -m yolo.infer_video `
  --mode damage `
  --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt `
  --source <path-to-road-video>.mp4 `
  --base-url http://127.0.0.1:8000
```
