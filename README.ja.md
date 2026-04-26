# 交通インシデント監視 API プラットフォーム

言語: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-Hant.md)

関連ドキュメント:

- ドキュメント一覧: [English](docs/document-index.md) | [日本語](docs/document-index.ja.md) | [繁體中文](docs/document-index.zh-Hant.md)
- デプロイ / 実行ガイド: [English](docs/deployment.md) | [日本語](docs/deployment.ja.md) | [繁體中文](docs/deployment.zh-Hant.md)
- 実装状況: [English](docs/implementation-vs-requirements-v2.en.md) | [日本語](docs/implementation-vs-requirements-v2.ja.md) | [繁體中文](docs/implementation-vs-requirements-v2.md)
- 要件定義書翻訳: [English](docs/requirements-spec.en.md) | [日本語](docs/requirements-spec.ja.md) | [繁體中文](docs/requirements-spec.zh-Hant.md) | [source PDF](docs/requirements_spec.md.pdf)
- AI 利用ログ: [English](docs/ai-log.md) | [日本語](docs/ai-log.ja.md) | [繁體中文](docs/ai-log.zh-Hant.md)
- AI 対話 source: [English](docs/ai-conversation-source.en.md) | [日本語](docs/ai-conversation-source.ja.md) | [繁體中文](docs/ai-conversation-source.zh-Hant.md) | [raw 抽出 Markdown](docs/ai-conversation-source.md) | [元 PDF](docs/Claude_geminiconversation.md.pdf)
- YOLO 動画テスト: [English](docs/yolo-video-test.md) | [日本語](docs/yolo-video-test.ja.md) | [繁體中文](docs/yolo-video-test.zh-Hant.md)
- 提出用アセットとデータ出典: [English](docs/submission-assets.md) | [日本語](docs/submission-assets.ja.md) | [繁體中文](docs/submission-assets.zh-Hant.md)
- public release notes: [English](docs/public-release-notes.md) | [日本語](docs/public-release-notes.ja.md) | [繁體中文](docs/public-release-notes.zh-Hant.md)

このリポジトリは、バックエンド課題に対する実装です。AI 動画解析システムから送られる交通インシデントを受け取り、SQLite に保存し、検索可能な REST API と Server-Sent Events (SSE) によるリアルタイム配信を提供します。

## 含まれるもの

- FastAPI による API 実装と `router / service / repository / schema` の分離
- SQLAlchemy + SQLite による永続化
- `source_event_id` による冪等なイベント受信
- フィルター、ソート、ページング付きのイベント一覧 API
- 戻し操作にも対応したステータス更新 API
- SSE によるリアルタイム Dashboard 更新
- English / 日本語 / 中文 を切り替えられる静的 HTML Dashboard。検索専用 Filter 説明、表示 / 該当件数、ページング、イベント種別の多言語表示、項目 tooltip、戻せるステータス操作にも対応
- デモ用のランダムイベント seed script
- `Dockerfile` と `docker-compose.yml`
- 主要 API フローの pytest
- `D:` 配下を使う YOLO 学習 / 推論パイプライン
- `docs/ai-log.md` の AI 利用ログ

## 技術選定

- **FastAPI**: API ドキュメント生成、async サポート、実装速度のバランスがよい。
- **SQLite**: 課題提出とローカル demo に十分で、セットアップが軽い。
- **SQLAlchemy 2.x**: DB モデルとクエリ制御を明確にできる。
- **SSE**: Dashboard への一方向リアルタイム通知という要件に合う。
- **Vanilla JS Dashboard**: フロントエンド依存を増やさず、動作確認に集中できる。

## API エンドポイント

| Method | Path | 目的 |
| --- | --- | --- |
| `POST` | `/events` | 新しいインシデントを受信 |
| `GET` | `/events` | フィルター、ソート、ページング付き一覧 |
| `GET` | `/events/{id}` | 1 件取得 |
| `PATCH` | `/events/{id}/status` | オペレーター対応ステータスを前後に更新 |
| `GET` | `/events/stream` | SSE でリアルタイム更新を購読 |

主な一覧フィルター:

- `severity`、`event_type`、`status`
- `camera_query`、`camera_id`、`source_event_id`、`highway_id`
- `detected_from/to`、`ingested_from/to`
- `min_delay_seconds`、`max_delay_seconds`
- `min_confidence`、`max_confidence`
- `sort_by=detected_at|ingested_at|updated_at|severity|confidence|detection_delay`
- `limit`、`offset`

## ローカル実行

```powershell
cd D:\Projects\traffic-incident-api
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload
```

開く場所:

- API docs: `http://localhost:8000/docs`
- Dashboard: `http://localhost:8000/ui/`

デモイベントを送る:

```powershell
.\.venv\Scripts\python scripts\seed.py
```

## Docker 実行

```powershell
cd D:\Projects\traffic-incident-api
docker compose up -d --build
```

起動されるサービス:

- `api`: `http://localhost:8000`
- `seed`: ランダムイベントを API に継続送信

seed を止めたい場合:

```powershell
docker compose stop seed
```

## テスト

```powershell
cd D:\Projects\traffic-incident-api
.\.venv\Scripts\pytest
```

直近の確認では `7 passed` です。

## レスポンス契約の要点

- `POST /events` は初回作成時に `201` を返す。
- 同じ `source_event_id` と同じ内容の再送は `200` + `meta.deduplicated=true` を返す。
- 同じ `source_event_id` で内容が異なる場合は `409` を返す。
- 同じステータスへの更新は `200` + `meta.noop=true` を返す。
- SSE は `incident.created` と `incident.status_updated` を送信する。

## YOLO 連携

YOLO 関連のデータセット、キャッシュ、学習結果、スナップショットは `D:\Datasets\traffic-incident` に置く前提です。
public GitHub release では、dataset 由来の MP4、snapshot、trained `.pt` weight は含めていません。`model-artifacts/` には training summary のみを残しています。RDD demo clip は local では `--dry-run` なしで確認済みで、`camera_id=CAM-YOLO-VIDEO-RDD` から `POST /events` 経由で `DEBRIS` event が 2 件保存されます。

```powershell
.\scripts\setup_training_env.ps1
.\.venv\Scripts\python.exe -m yolo.download_datasets --show-paths
.\.venv\Scripts\python.exe -m yolo.prepare_mio_tcd
.\.venv\Scripts\python.exe -m yolo.prepare_rdd2022
.\.venv\Scripts\python.exe -m yolo.train --profile mio-localization
.\.venv\Scripts\python.exe -m yolo.train --profile rdd2022
```

動画推論から API にイベントを送る例:

```powershell
.\.venv\Scripts\python.exe -m yolo.infer_video --mode vehicle --weights D:\Datasets\traffic-incident\runs\mio-localization\<run>\weights\best.pt --source D:\path\to\highway.mp4
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights D:\Datasets\traffic-incident\runs\rdd2022\<run>\weights\best.pt --source D:\path\to\road.mp4
```

提出用 demo を最短で確認する場合:

```powershell
docker compose up -d --build
docker compose stop seed
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights D:\Datasets\traffic-incident\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt --source D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.mp4 --base-url http://127.0.0.1:8000 --camera-id CAM-YOLO-VIDEO-RDD --confidence 0.25 --frame-stride 1 --cooldown-seconds 5 --annotated-output D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.boxes.mp4
Invoke-RestMethod 'http://127.0.0.1:8000/events?camera_id=CAM-YOLO-VIDEO-RDD&sort_by=detected_at&order=desc&limit=10&offset=0' | ConvertTo-Json -Depth 12
```

結果には `event_type=DEBRIS`、`camera_id=CAM-YOLO-VIDEO-RDD`、`extra_payload.source=yolo.detector` が含まれます。Swagger は `http://127.0.0.1:8000/docs`、Dashboard は `http://127.0.0.1:8000/ui/` で確認できます。

## トレードオフ

- 認証・認可は課題範囲外として明示的に除外。
- SQLite は提出用 demo に適しているが、本番では PostgreSQL を想定。
- WebSocket ではなく SSE を採用し、一方向の即時通知を簡潔に実現。
- `source_event_id` を検知システムと API 間の冪等キーとして扱う。
- Dashboard はデザイン評価ではなく、API とリアルタイム更新の可視化を目的にしている。

## 本番化するなら

- API key または JWT 認証
- rate limiting と監査ログ
- 画像の object storage 保存
- PostgreSQL 移行
- retry queue / background worker
- モデル評価と detector pipeline の監視
