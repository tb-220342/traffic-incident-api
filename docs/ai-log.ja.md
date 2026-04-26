# AI 利用ログ

言語: [English](ai-log.md) | [日本語](ai-log.ja.md) | [繁體中文](ai-log.zh-Hant.md)

このファイルは、本課題の開発で AI 支援をどのように利用したかをまとめたものです。
Claude / Gemini との対話原文は `docs/ai-conversation-source.md` に抽出しており、元 PDF は `docs/Claude_geminiconversation.md.pdf` に保存しています。

## 参照した入力

- `C:\Users\85260\Downloads\Back-End_Candidate_Evaluation.pdf`
- `C:\Users\85260\Downloads\requirements_spec.md.pdf`
- `C:\Users\85260\Downloads\Claude_geminiconversation.md.pdf`

## 作業の流れ

1. 評価課題を読み取り、必須スコープを確認しました。
   - 検知システムからイベントを受け取る。
   - オペレーター向けに検索可能な API を提供する。
   - 「Speed matters」という文脈から即時性を重視する。
2. 追加の要件定義書を読み取りました。
   - FastAPI + SQLite + SQLAlchemy + SSE を採用する方針を確認。
   - Dashboard、seed script、Docker、テストは加点要素として扱う。
   - YOLO 統合は任意だが、実装する場合は end-to-end に近い形にする。
3. 実装方針を決めました。
   - まず core API と SSE を実装する。
   - 次に軽量 Dashboard でリアルタイム動作を見せる。
   - その後、テスト、README、Docker、seed script を追加する。
4. `D:\Projects\traffic-incident-api` にプロジェクトを作成しました。
5. ローカル検証を行い、テスト中に見つかった問題を修正しました。
6. 学習対応版として YOLO 関連機能を拡張しました。
   - MIO-TCD、RDD2022、TRANCOS の downloader を追加。
   - MIO-TCD と RDD2022 のデータ変換 script を追加。
   - YOLO 学習コマンドと動画推論から API に送信する utility を追加。
   - 大きな dataset/cache/run/snapshot は `D:\Datasets\traffic-incident` に配置。
   - RDD2022 の動画推論を `--dry-run` なしで実行し、API 経由で `DEBRIS` event が 2 件保存されることを確認。
7. 提出前の整備として、Dashboard と Markdown 文書を English / 日本語 / 繁體中文 に対応させました。

## 主な設計判断

- Dashboard への一方向通知なので、WebSocket ではなく SSE を採用しました。
- 課題提出用に軽く動かせることを重視し、SQLite を採用しました。
- 明示的なステータス遷移ルールを維持しつつ、UI 確認後に誤操作から戻せる rollback も追加しました。
- API は成功時 `{ success, data, meta }`、失敗時 `{ success, error }` の形式に統一しました。
- 検知システムからの重複送信に備え、`source_event_id` を冪等キーにしました。
- MIO-TCD は車両検出、RDD2022 は路面異常を `DEBRIS` 相当の危険イベントとして扱うために使用しました。
- C ドライブ容量を圧迫しないよう、ML 関連の大きなファイルは `D:` に配置しました。

## 今回の範囲外

- 認証・認可
- rate limiting や本番 observability などの運用機能
- 実道路動画に対する正式な detector 精度評価
