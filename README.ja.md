# 交通インシデント監視 API プラットフォーム

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](#技術選定)
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white)](#api-エンドポイント)
[![SQLite](https://img.shields.io/badge/SQLite-Persistence-003B57?logo=sqlite&logoColor=white)](#ローカル実行)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)](#docker-実行)
[![SSE](https://img.shields.io/badge/Realtime-SSE-111827)](#レスポンス契約の要点)
[![YOLO](https://img.shields.io/badge/YOLO-Optional%20Pipeline-FF6B00)](#yolo-連携)

言語: [English](README.md) | [日本語](README.ja.md) | [繁體中文](README.zh-Hant.md)

交通インシデント監視プラットフォームのバックエンド課題実装です。AI 動画解析から送られる incident を受信し、SQLite に保存し、検索可能な REST API と SSE によるリアルタイム Dashboard 更新を提供します。

> [!NOTE]
> 公開リポジトリとして安全に共有できるよう、生データセット、データセット由来 MP4、スナップショット、学習済み `.pt` weight、ローカル `.env`、個人端末固有の path は repository に含めていません。

## レビュー用クイックパス

| 目的 | リンク / コマンド |
| --- | --- |
| デモ起動 | `docker compose up -d --build` |
| API ドキュメント | `http://127.0.0.1:8000/docs` |
| ダッシュボード | `http://127.0.0.1:8000/ui/` |
| 実装完成度 | [実装状況 vs 要件](docs/implementation-vs-requirements-v2.ja.md) |
| 実行手順 | [デプロイ / 実行ガイド](docs/deployment.ja.md) |
| 全文書一覧 | [ドキュメント一覧](docs/document-index.ja.md) |

## ドキュメントハブ

| 文書 | 英語 | 日本語 | 繁體中文 |
| --- | --- | --- | --- |
| ドキュメント一覧 | [EN](docs/document-index.md) | [JA](docs/document-index.ja.md) | [ZH](docs/document-index.zh-Hant.md) |
| デプロイ / 実行ガイド | [EN](docs/deployment.md) | [JA](docs/deployment.ja.md) | [ZH](docs/deployment.zh-Hant.md) |
| 実装状況 | [EN](docs/implementation-vs-requirements-v2.en.md) | [JA](docs/implementation-vs-requirements-v2.ja.md) | [ZH](docs/implementation-vs-requirements-v2.md) |
| 要件定義書 | [EN](docs/requirements-spec.en.md) | [JA](docs/requirements-spec.ja.md) | [ZH](docs/requirements-spec.zh-Hant.md) |
| AI 利用ログ | [EN](docs/ai-log.md) | [JA](docs/ai-log.ja.md) | [ZH](docs/ai-log.zh-Hant.md) |
| AI 対話ソース | [EN](docs/ai-conversation-source.en.md) | [JA](docs/ai-conversation-source.ja.md) | [ZH](docs/ai-conversation-source.zh-Hant.md) |
| YOLO 動画テスト | [EN](docs/yolo-video-test.md) | [JA](docs/yolo-video-test.ja.md) | [ZH](docs/yolo-video-test.zh-Hant.md) |
| 提出アセットと出典 | [EN](docs/submission-assets.md) | [JA](docs/submission-assets.ja.md) | [ZH](docs/submission-assets.zh-Hant.md) |
| 公開リリースノート | [EN](docs/public-release-notes.md) | [JA](docs/public-release-notes.ja.md) | [ZH](docs/public-release-notes.zh-Hant.md) |

原資料: [要件 PDF](docs/requirements_spec.md.pdf)、[AI 対話 PDF](docs/Claude_geminiconversation.md.pdf)、[AI 対話の raw 抽出 Markdown](docs/ai-conversation-source.md)。

## 含まれるもの

| 領域 | 内容 |
| --- | --- |
| API | FastAPI、Pydantic 検証、`source_event_id` による冪等受信、一覧 / 詳細 / ステータス API |
| リアルタイム | `incident.created` / `incident.status_updated` を SSE 配信 |
| 永続化 | SQLAlchemy + SQLite、Docker volume による保存 |
| ダッシュボード | Vanilla JS、EN/JA/ZH、フィルター説明、ページング、tooltip、戻せるステータス操作 |
| デモ運用 | Docker Compose、seed script、Swagger UI、同梱 demo DB |
| YOLO 拡張 | download / prepare / train / infer / API post の pipeline |
| 証跡 | tests、screenshots、AI logs、要件比較、公開リリースノート |

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
cd <repo-root>
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\uvicorn app.main:app --reload
```

開く場所:

- API ドキュメント: `http://localhost:8000/docs`
- ダッシュボード: `http://localhost:8000/ui/`

デモイベントを送る:

```powershell
.\.venv\Scripts\python scripts\seed.py
```

## Docker 実行

```powershell
cd <repo-root>
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
cd <repo-root>
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

YOLO 関連のデータセット、キャッシュ、学習結果、スナップショットは `<DATA_ROOT>` に置く前提です。
`<DATA_ROOT>` は repository 外の ML data directory で、default は `../traffic-incident-data`、または `TRAFFIC_DATASETS_ROOT` で指定した path です。
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
.\.venv\Scripts\python.exe -m yolo.infer_video --mode vehicle --weights <DATA_ROOT>\runs\mio-localization\<run>\weights\best.pt --source <path-to-highway-video>.mp4
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights <DATA_ROOT>\runs\rdd2022\<run>\weights\best.pt --source <path-to-road-video>.mp4
```

提出用デモを最短で確認する場合:

```powershell
docker compose up -d --build
docker compose stop seed
.\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights <DATA_ROOT>\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt --source <DATA_ROOT>\yolovideotest\rdd_damage_short.mp4 --base-url http://127.0.0.1:8000 --camera-id CAM-YOLO-VIDEO-RDD --confidence 0.25 --frame-stride 1 --cooldown-seconds 5 --annotated-output <DATA_ROOT>\yolovideotest\rdd_damage_short.boxes.mp4
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
