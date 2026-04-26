# ドキュメント一覧

言語: [English](document-index.md) | [日本語](document-index.ja.md) | [繁體中文](document-index.zh-Hant.md)

このページは提出文書のナビゲーションです。README が入口なら、このページは全体の案内板です。

> [!TIP]
> 最短 review では `README.ja.md`、Docker Compose、`/docs`、`/ui/`、実装状況、public release notes の順に見ると全体像を掴みやすいです。

## Fast Review Route

| Step | Read / Open | 意味 |
| --- | --- | --- |
| 1 | [README.ja.md](../README.ja.md) | 概要と quick start |
| 2 | [Deployment guide](deployment.ja.md) | 再現可能な実行手順 |
| 3 | [Implementation status](implementation-vs-requirements-v2.ja.md) | 要件ごとの完成度 |
| 4 | [Public release notes](public-release-notes.ja.md) | dataset / weight の公開方針 |
| 5 | [AI workflow log](ai-log.ja.md) | AI 利用開示 |

## 最初に読むもの

- `README.md`: English の overview。quick start、API summary、Docker/local run、YOLO-to-API demo、trade-off を説明。
- `README.ja.md`: 日本語 README。
- `README.zh-Hant.md`: 繁體中文 README。

## 提出 / review 用文書

| Document | Purpose |
| --- | --- |
| [deployment.md](deployment.md) | Docker Compose、local Python、DB persistence、YOLO write-to-API 確認 |
| [deployment.ja.md](deployment.ja.md) | 日本語 deployment guide |
| [deployment.zh-Hant.md](deployment.zh-Hant.md) | 繁體中文 deployment guide |
| [requirements-spec.en.md](requirements-spec.en.md) | English の要件定義書 |
| [requirements-spec.ja.md](requirements-spec.ja.md) | 日本語の要件定義書 |
| [requirements-spec.zh-Hant.md](requirements-spec.zh-Hant.md) | 繁體中文の要件定義書 |
| [requirements_spec.md.pdf](requirements_spec.md.pdf) | 要件定義書の元 PDF |
| [implementation-vs-requirements-v2.en.md](implementation-vs-requirements-v2.en.md) | English の完成度 checklist |
| [implementation-vs-requirements-v2.ja.md](implementation-vs-requirements-v2.ja.md) | 日本語の完成度 checklist |
| [implementation-vs-requirements-v2.md](implementation-vs-requirements-v2.md) | 繁體中文の完成度 checklist |

## AI 利用記録

| Document | Purpose |
| --- | --- |
| [ai-log.md](ai-log.md) | English の AI workflow summary |
| [ai-log.ja.md](ai-log.ja.md) | 日本語の AI workflow summary |
| [ai-log.zh-Hant.md](ai-log.zh-Hant.md) | 繁體中文の AI workflow summary |
| [ai-conversation-source.en.md](ai-conversation-source.en.md) | Claude / Gemini 対話 source の English translation |
| [ai-conversation-source.ja.md](ai-conversation-source.ja.md) | Claude / Gemini 対話 source の日本語 translation |
| [ai-conversation-source.zh-Hant.md](ai-conversation-source.zh-Hant.md) | Claude / Gemini 対話 source の繁體中文 translation |
| [ai-conversation-source.md](ai-conversation-source.md) | Claude / Gemini 対話の raw 抽出 text |
| [Claude_geminiconversation.md.pdf](Claude_geminiconversation.md.pdf) | Claude / Gemini 対話の元 PDF |

## YOLO / data evidence

| Document | Purpose |
| --- | --- |
| [yolo-video-test.md](yolo-video-test.md) | YOLO video test、dry-run command、API write demo |
| [yolo-video-test.ja.md](yolo-video-test.ja.md) | 日本語 YOLO video test guide |
| [yolo-video-test.zh-Hant.md](yolo-video-test.zh-Hant.md) | 繁體中文 YOLO video test guide |
| [submission-assets.md](submission-assets.md) | asset、除外 asset、data source、demo DB source |
| [submission-assets.ja.md](submission-assets.ja.md) | 日本語 asset/source guide |
| [submission-assets.zh-Hant.md](submission-assets.zh-Hant.md) | 繁體中文 asset/source guide |
| [public-release-notes.md](public-release-notes.md) | public GitHub release policy |
| [public-release-notes.ja.md](public-release-notes.ja.md) | 日本語 public release notes |
| [public-release-notes.zh-Hant.md](public-release-notes.zh-Hant.md) | 繁體中文 public release notes |

## 画面 evidence

- `docs/dashboard-smoke.png`: dashboard smoke-test screenshot。
- `docs/dashboard-i18n-smoke.png`: dashboard i18n smoke-test screenshot。

## Markdown 以外の運用 file

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
