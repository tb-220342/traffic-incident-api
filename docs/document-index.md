# Document Index

Language: [English](document-index.md) | [日本語](document-index.ja.md) | [繁體中文](document-index.zh-Hant.md)

Use this page as the navigation map for the submission. If the README is the lobby, this is the directory board.

> [!TIP]
> For a fast review, read `README.md`, run Docker Compose, open `/docs` and `/ui/`, then skim the implementation status and public release notes.

## Fast Review Route

| Step | Read / Open | Why it matters |
| --- | --- | --- |
| 1 | [README.md](../README.md) | Project overview and quick start |
| 2 | [Deployment guide](deployment.md) | Reproducible run instructions |
| 3 | [Implementation status](implementation-vs-requirements-v2.en.md) | Requirement-by-requirement completion view |
| 4 | [Public release notes](public-release-notes.md) | Dataset and weight redistribution policy |
| 5 | [AI workflow log](ai-log.md) | Required AI usage disclosure |

## Start Here

- `README.md`: main English overview, quick start, API summary, Docker/local run, YOLO-to-API demo, trade-offs.
- `README.ja.md`: Japanese README.
- `README.zh-Hant.md`: Traditional Chinese README.

## Delivery / Review Documents

| Document | Purpose |
| --- | --- |
| [deployment.md](deployment.md) | Docker Compose, local Python, DB persistence, and YOLO write-to-API verification |
| [deployment.ja.md](deployment.ja.md) | Japanese deployment guide |
| [deployment.zh-Hant.md](deployment.zh-Hant.md) | Traditional Chinese deployment guide |
| [requirements-spec.en.md](requirements-spec.en.md) | Requirements specification in English |
| [requirements-spec.ja.md](requirements-spec.ja.md) | Requirements specification in Japanese |
| [requirements-spec.zh-Hant.md](requirements-spec.zh-Hant.md) | Requirements specification in Traditional Chinese |
| [requirements_spec.md.pdf](requirements_spec.md.pdf) | Original requirements specification PDF |
| [implementation-vs-requirements-v2.en.md](implementation-vs-requirements-v2.en.md) | Implementation completion checklist in English |
| [implementation-vs-requirements-v2.ja.md](implementation-vs-requirements-v2.ja.md) | Implementation completion checklist in Japanese |
| [implementation-vs-requirements-v2.md](implementation-vs-requirements-v2.md) | Implementation completion checklist in Traditional Chinese |

## AI Usage Records

| Document | Purpose |
| --- | --- |
| [ai-log.md](ai-log.md) | Summarized AI workflow log in English |
| [ai-log.ja.md](ai-log.ja.md) | Summarized AI workflow log in Japanese |
| [ai-log.zh-Hant.md](ai-log.zh-Hant.md) | Summarized AI workflow log in Traditional Chinese |
| [ai-conversation-source.en.md](ai-conversation-source.en.md) | English translation of the Claude/Gemini conversation source |
| [ai-conversation-source.ja.md](ai-conversation-source.ja.md) | Japanese translation of the Claude/Gemini conversation source |
| [ai-conversation-source.zh-Hant.md](ai-conversation-source.zh-Hant.md) | Traditional Chinese translation of the Claude/Gemini conversation source |
| [ai-conversation-source.md](ai-conversation-source.md) | Raw extracted Claude/Gemini conversation text |
| [Claude_geminiconversation.md.pdf](Claude_geminiconversation.md.pdf) | Original Claude/Gemini conversation PDF |

## YOLO / Data Evidence

| Document | Purpose |
| --- | --- |
| [yolo-video-test.md](yolo-video-test.md) | YOLO video test clips, dry-run commands, and verified API write demo |
| [yolo-video-test.ja.md](yolo-video-test.ja.md) | Japanese YOLO video test guide |
| [yolo-video-test.zh-Hant.md](yolo-video-test.zh-Hant.md) | Traditional Chinese YOLO video test guide |
| [submission-assets.md](submission-assets.md) | Included/excluded assets, data sources, demo DB source |
| [submission-assets.ja.md](submission-assets.ja.md) | Japanese asset/source guide |
| [submission-assets.zh-Hant.md](submission-assets.zh-Hant.md) | Traditional Chinese asset/source guide |
| [public-release-notes.md](public-release-notes.md) | Public GitHub release policy for dataset-derived media and weights |
| [public-release-notes.ja.md](public-release-notes.ja.md) | Japanese public release notes |
| [public-release-notes.zh-Hant.md](public-release-notes.zh-Hant.md) | Traditional Chinese public release notes |

## Visual Evidence

| File | Purpose |
| --- | --- |
| [dashboard-smoke.png](dashboard-smoke.png) | Dashboard smoke-test screenshot |
| [dashboard-i18n-smoke.png](dashboard-i18n-smoke.png) | Dashboard i18n smoke-test screenshot |

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
