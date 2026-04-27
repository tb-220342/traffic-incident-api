# アーキテクチャレビュー用メモ

言語: [English](architecture-review-notes.md) | [日本語](architecture-review-notes.ja.md) | [繁體中文](architecture-review-notes.zh-Hant.md)

[ドキュメント一覧](document-index.ja.md) に戻る | [Project README](../README.ja.md)

> [!NOTE]
> このメモは、面接課題で見られやすい評価点に対応しています。API 設計、schema / data model、リアルタイム通知、技術選定の trade-off、本番化に向けた改善点をまとめています。

## 1. API 設計

API は、課題シナリオの event lifecycle に合わせています。検知システムが incident を作成し、operator が検索し、対応状況を更新する流れです。

| Endpoint | 設計理由 |
| --- | --- |
| `POST /events` | AI / 動画解析側から検知 event を受け取る。Pydantic で入力を検証し、受理した event を保存する。 |
| `GET /events` | operator 向け一覧。filter、sort、pagination により、管制センターの検索・triage に対応する。 |
| `GET /events/{id}` | 1 件の incident 詳細を確認する。 |
| `PATCH /events/{id}/status` | operator が確認・対応・解決状況を更新するための endpoint。誤操作に備え、必要に応じて status を戻せる。 |
| `GET /events/stream` | 新規 event と status 更新を dashboard client に stream 配信する。 |

`source_event_id` は idempotency key として扱います。検知システムや retry 処理では同じ event が再送される可能性があるためです。同じ `source_event_id` かつ同じ payload は安全な重複として扱い、内容が衝突する場合は `409 Conflict` を返します。

## 2. データモデル

データモデルは小さく保ちつつ、operator が「何が起きたか」「どこで起きたか」「どれくらい急ぐべきか」「検知はどの程度信用できるか」を判断できる情報を持たせています。

| Field group | 設計理由 |
| --- | --- |
| 識別子 | `id` は内部 UUID。`source_event_id` は検知元との対応と冪等性に使う。 |
| Incident 種別 | `event_type` は停止車両、落下物、渋滞、逆走、歩行者検知などを表す。 |
| 優先度 | `severity` により、重大 event を優先して確認できる。 |
| Operator workflow | `status`、`status_note`、`updated_at` により、対応状況と操作履歴を追える。 |
| 時刻 | `detected_at` と `ingested_at` を分けることで、検知から API 受信までの遅延を計算できる。 |
| 位置 | `camera_id`、`highway_id`、`road_marker`、`lane_no`、緯度経度により、人間の確認と将来の地図連携に対応する。 |
| 証跡 | `description`、`image_url`、`extra_payload` で context を残し、schema を早期に固定しすぎない。 |
| ML 信頼度 | `confidence` により、低 confidence の event を慎重に扱える。 |

緯度経度は optional にしています。交通システムでは GPS ではなく camera、road marker、lane で incident を識別する場合もあるためです。

## 3. リアルタイム通知方式

課題には「Speed matters」とあり、operator が早く event を見られるほど対応も早くなります。そのため Server-Sent Events (SSE) を採用しました。

SSE が合う理由は、今回のリアルタイム処理が主に一方向だからです。dashboard は `incident.created` と `incident.status_updated` を受け取れればよく、複雑な双方向通信は必要ありません。

Polling ではなく SSE にした理由:

- polling は遅延が出やすく、不要なリクエストも増える。
- SSE は API が event を受理または更新した直後に push できる。
- demo 環境でも動かしやすく、browser や terminal から確認しやすい。

WebSocket ではなく SSE にした理由:

- WebSocket は複雑な双方向通信には有効。
- 今回は server から dashboard への一方向通知が中心。
- SSE の方が構成を小さく保ちながら、speed requirement に答えられる。

## 4. SQLite 採用理由

SQLite は interview / demo 用の選択です。本番の交通監視基盤に最適な DB と主張しているわけではありません。

今回 SQLite が合理的な理由:

- 課題文に「even SQLite is perfectly fine」と明記されている。
- reviewer が DB server を用意せずに clone 後すぐ起動できる。
- Docker Compose の volume mount で SQLite file を永続化できる。
- repository layer を分けているため、将来 PostgreSQL に移行しても public API contract は維持しやすい。

一方で、高頻度 write、多数 instance、本番運用には SQLite は向きません。この制約は hidden risk ではなく、production follow-up として明示しています。

## 5. 本番化に向けた改善点

本番化する場合は、以下を追加・変更します。

| 領域 | 改善内容 |
| --- | --- |
| Database | SQLite を PostgreSQL に置き換え、Alembic migration を追加する。 |
| Reliability | detector traffic が増える場合、event ingestion の前段に queue / stream を置く。 |
| Authentication | 検知システムと operator 向けに API key、OAuth、service-to-service auth を追加する。 |
| Authorization | detector の書き込み権限と operator の閲覧・更新権限を分ける。 |
| Observability | metrics、tracing、structured logs、ingestion latency / SSE failure alert を追加する。 |
| Scalability | 複数 instance の SSE broadcast には Redis、PostgreSQL LISTEN/NOTIFY、message broker を使う。 |
| Operations | backup、retention policy、deployment pipeline、incident-response runbook を整備する。 |
| ML integration | model / dataset version、inference provenance、false positive / false negative monitoring を追加する。 |

## まとめ

現在の architecture は、面接課題向けに意図的に小さく、実行しやすく、end-to-end に見せられる構成です。API と data model は traffic incident workflow に合っており、SSE は speed requirement に対応し、SQLite は review の再現性を高めます。本番化に必要な差分も明示しているため、scope control と trade-off を説明しやすい構成です。
