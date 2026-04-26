# ドキュメント一覧

このページは repository 内の文書の地図です。

## 最初に読むもの

- `README.md`: English の overview。quick start、API summary、Docker/local run、YOLO-to-API demo、trade-off を説明。
- `README.ja.md`: 日本語 README。
- `README.zh-Hant.md`: 繁體中文 README。

## 提出 / review 用文書

- `docs/deployment.md`: Docker Compose、local Python、database persistence、YOLO write-to-API 確認を含む実行 / deployment guide。
- `docs/deployment.ja.md`: 日本語 deployment guide。
- `docs/deployment.zh-Hant.md`: 繁體中文 deployment guide。
- `docs/implementation-vs-requirements-v2.en.md`: English の実装 vs 要件 status。
- `docs/implementation-vs-requirements-v2.ja.md`: 日本語の実装 vs 要件 status。
- `docs/implementation-vs-requirements-v2.md`: 繁體中文の実装 vs 要件 status。

## AI 利用記録

- `docs/ai-log.md`: English の AI workflow summary。
- `docs/ai-log.ja.md`: 日本語の AI workflow summary。
- `docs/ai-log.zh-Hant.md`: 繁體中文の AI workflow summary。
- `docs/ai-conversation-source.md`: Claude / Gemini 対話の抽出 text。
- `docs/Claude_geminiconversation.md.pdf`: Claude / Gemini 対話の元 PDF。

## YOLO / data evidence

- `docs/yolo-video-test.md`: YOLO 動画 clip、dry-run command、API 書き込み確認済み demo。
- `docs/yolo-video-test.ja.md`: 日本語 YOLO 動画 test guide。
- `docs/yolo-video-test.zh-Hant.md`: 繁體中文 YOLO 動画 test guide。
- `docs/submission-assets.md`: repository に含めた asset、除外した asset、データ出典、demo DB source。
- `docs/submission-assets.ja.md`: 日本語 asset/source guide。
- `docs/submission-assets.zh-Hant.md`: 繁體中文 asset/source guide。
- `docs/public-release-notes.md`: public GitHub release における dataset 由来 media / weight の扱い。
- `docs/public-release-notes.ja.md`: 日本語 public release notes。
- `docs/public-release-notes.zh-Hant.md`: 繁體中文 public release notes。

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
