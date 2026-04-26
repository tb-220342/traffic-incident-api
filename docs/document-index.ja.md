# ドキュメント一覧

言語: [English](document-index.md) | [日本語](document-index.ja.md) | [繁體中文](document-index.zh-Hant.md)

このページは提出文書のナビゲーションです。README が入口なら、このページは全体の案内板です。

> [!TIP]
> 最短レビューでは `README.ja.md`、Docker Compose、`/docs`、`/ui/`、実装状況、公開リリースノートの順に見ると全体像を掴みやすいです。

## 最短レビュールート

| 手順 | 読む / 開く | 意味 |
| --- | --- | --- |
| 1 | [README.ja.md](../README.ja.md) | 概要と quick start |
| 2 | [デプロイ / 実行ガイド](deployment.ja.md) | 再現可能な実行手順 |
| 3 | [実装状況](implementation-vs-requirements-v2.ja.md) | 要件ごとの完成度 |
| 4 | [公開リリースノート](public-release-notes.ja.md) | データセット / weight の公開方針 |
| 5 | [AI 利用ログ](ai-log.ja.md) | AI 利用開示 |

## 最初に読むもの

- `README.md`: English の概要。quick start、API summary、Docker/local run、YOLO-to-API demo、trade-off を説明。
- `README.ja.md`: 日本語 README。
- `README.zh-Hant.md`: 繁體中文 README。

## 提出 / レビュー用文書

| 文書 | 目的 |
| --- | --- |
| [deployment.md](deployment.md) | Docker Compose、ローカル Python、DB 永続化、YOLO から API への書き込み確認 |
| [deployment.ja.md](deployment.ja.md) | 日本語デプロイ / 実行ガイド |
| [deployment.zh-Hant.md](deployment.zh-Hant.md) | 繁體中文デプロイ / 実行ガイド |
| [requirements-spec.en.md](requirements-spec.en.md) | English の要件定義書 |
| [requirements-spec.ja.md](requirements-spec.ja.md) | 日本語の要件定義書 |
| [requirements-spec.zh-Hant.md](requirements-spec.zh-Hant.md) | 繁體中文の要件定義書 |
| [requirements_spec.md.pdf](requirements_spec.md.pdf) | 要件定義書の元 PDF |
| [implementation-vs-requirements-v2.en.md](implementation-vs-requirements-v2.en.md) | English の完成度チェックリスト |
| [implementation-vs-requirements-v2.ja.md](implementation-vs-requirements-v2.ja.md) | 日本語の完成度チェックリスト |
| [implementation-vs-requirements-v2.md](implementation-vs-requirements-v2.md) | 繁體中文の完成度チェックリスト |

## AI 利用記録

| 文書 | 目的 |
| --- | --- |
| [ai-log.md](ai-log.md) | English の AI 利用概要 |
| [ai-log.ja.md](ai-log.ja.md) | 日本語の AI 利用概要 |
| [ai-log.zh-Hant.md](ai-log.zh-Hant.md) | 繁體中文の AI 利用概要 |
| [ai-conversation-source.en.md](ai-conversation-source.en.md) | Claude / Gemini 対話ソースの English 翻訳 |
| [ai-conversation-source.ja.md](ai-conversation-source.ja.md) | Claude / Gemini 対話ソースの日本語翻訳 |
| [ai-conversation-source.zh-Hant.md](ai-conversation-source.zh-Hant.md) | Claude / Gemini 対話ソースの繁體中文翻訳 |
| [ai-conversation-source.md](ai-conversation-source.md) | Claude / Gemini 対話の raw 抽出テキスト |
| [Claude_geminiconversation.md.pdf](Claude_geminiconversation.md.pdf) | Claude / Gemini 対話の元 PDF |

## YOLO / データ証跡

| 文書 | 目的 |
| --- | --- |
| [yolo-video-test.md](yolo-video-test.md) | YOLO 動画テスト、dry-run コマンド、API 書き込みデモ |
| [yolo-video-test.ja.md](yolo-video-test.ja.md) | 日本語 YOLO 動画テストガイド |
| [yolo-video-test.zh-Hant.md](yolo-video-test.zh-Hant.md) | 繁體中文 YOLO 動画テストガイド |
| [submission-assets.md](submission-assets.md) | 含めた asset、除外した asset、データ出典、demo DB 出典 |
| [submission-assets.ja.md](submission-assets.ja.md) | 日本語 asset / 出典ガイド |
| [submission-assets.zh-Hant.md](submission-assets.zh-Hant.md) | 繁體中文 asset / 出典ガイド |
| [public-release-notes.md](public-release-notes.md) | public GitHub release 方針 |
| [public-release-notes.ja.md](public-release-notes.ja.md) | 日本語公開リリースノート |
| [public-release-notes.zh-Hant.md](public-release-notes.zh-Hant.md) | 繁體中文公開リリースノート |

## 画面証跡

- `docs/dashboard-smoke.png`: dashboard smoke-test screenshot。
- `docs/dashboard-i18n-smoke.png`: dashboard i18n smoke-test screenshot。

## Markdown 以外の運用ファイル

- `Dockerfile`: FastAPI API の container image 定義。
- `docker-compose.yml`: `api` と optional `seed` service を起動。
- `.env.example`: environment variable example。
- `.gitignore`: cache、local DB、raw dataset、dataset 由来 media、YOLO weight、大きい intermediate file を除外する設定。
- `.dockerignore`: Docker build context を小さくする設定。
- `.gitattributes`: MP4、DB、PT、PDF、PNG などを binary として扱う設定。
- `requirements.txt`: API/runtime Python dependencies。
- `requirements-ml.txt`: YOLO/ML dependencies。

## 完全な production runbook ではないもの

これは interview/demo submission であり、本番運用 service ではありません。production follow-up は `docs/deployment.ja.md` に書いていますが、cloud deployment、authentication rollout、monitoring、backup、incident-response runbook は今回の scope 外です。
