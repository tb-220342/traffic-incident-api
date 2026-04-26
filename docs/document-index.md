# Document Index

Use this page as the map for the repository documents.

## Start Here

- `README.md`: main English overview, quick start, API summary, Docker/local run, YOLO-to-API demo, trade-offs.
- `README.ja.md`: Japanese README.
- `README.zh-Hant.md`: Traditional Chinese README.

## Delivery / Review Documents

- `docs/deployment.md`: how to run/deploy the demo with Docker Compose, local Python, database persistence, and YOLO write-to-API verification.
- `docs/deployment.ja.md`: Japanese deployment guide.
- `docs/deployment.zh-Hant.md`: Traditional Chinese deployment guide.
- `docs/implementation-vs-requirements-v2.en.md`: implementation vs requirements status in English.
- `docs/implementation-vs-requirements-v2.ja.md`: implementation vs requirements status in Japanese.
- `docs/implementation-vs-requirements-v2.md`: implementation vs requirements status in Traditional Chinese.

## AI Usage Records

- `docs/ai-log.md`: summarized AI workflow log in English.
- `docs/ai-log.ja.md`: summarized AI workflow log in Japanese.
- `docs/ai-log.zh-Hant.md`: summarized AI workflow log in Traditional Chinese.
- `docs/ai-conversation-source.md`: extracted raw Claude/Gemini conversation text.
- `docs/Claude_geminiconversation.md.pdf`: original Claude/Gemini conversation PDF.

## YOLO / Data Evidence

- `docs/yolo-video-test.md`: YOLO video test clips, dry-run commands, and verified API write demo in English.
- `docs/yolo-video-test.ja.md`: Japanese YOLO video test guide.
- `docs/yolo-video-test.zh-Hant.md`: Traditional Chinese YOLO video test guide.
- `docs/submission-assets.md`: included assets, excluded assets, data sources, demo DB source in English.
- `docs/submission-assets.ja.md`: Japanese asset/source guide.
- `docs/submission-assets.zh-Hant.md`: Traditional Chinese asset/source guide.
- `docs/public-release-notes.md`: public GitHub release policy for dataset-derived media and weights in English.
- `docs/public-release-notes.ja.md`: Japanese public release notes.
- `docs/public-release-notes.zh-Hant.md`: Traditional Chinese public release notes.

## Visual Evidence

- `docs/dashboard-smoke.png`: dashboard smoke-test screenshot.
- `docs/dashboard-i18n-smoke.png`: dashboard i18n smoke-test screenshot.

## Non-Markdown Operational Files

- `Dockerfile`: container image definition for the FastAPI API.
- `docker-compose.yml`: starts `api` and optional `seed` services.
- `.env.example`: environment variable example.
- `.gitignore`: excludes caches, local DB, raw datasets, dataset-derived media, YOLO weights, and large intermediate files.
- `.dockerignore`: keeps Docker build context small.
- `.gitattributes`: marks binary assets such as MP4, DB, PT, PDF, and PNG as binary.
- `requirements.txt`: API/runtime Python dependencies.
- `requirements-ml.txt`: YOLO/ML dependencies.

## What Is Not Documented As A Full Production Runbook

This is an interview/demo submission, not a production service. The production follow-up items are described in `docs/deployment.md`, but complete cloud deployment, authentication rollout, monitoring, backups, and incident-response runbooks are intentionally out of scope.
