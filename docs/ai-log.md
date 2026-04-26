# AI Workflow Log

Languages: [English](ai-log.md) | [日本語](ai-log.ja.md) | [繁體中文](ai-log.zh-Hant.md)

This file summarizes how AI assistance was used while building the assignment.
The raw Claude/Gemini conversation source is included as `docs/ai-conversation-source.md`, with the original PDF kept at `docs/Claude_geminiconversation.md.pdf`.

## Inputs referenced

- `C:\Users\85260\Downloads\Back-End_Candidate_Evaluation.pdf`
- `C:\Users\85260\Downloads\requirements_spec.md.pdf`
- `C:\Users\85260\Downloads\Claude_geminiconversation.md.pdf`

## Workflow summary

1. Extracted and reviewed the evaluation brief to understand the mandatory scope:
   - Accept events from a detection system
   - Expose queryable APIs for operators
   - Prioritize speed and operational usefulness
2. Extracted and reviewed the custom requirements specification:
   - Confirmed the preferred stack was FastAPI + SQLite + SQLAlchemy + SSE
   - Confirmed nice-to-have items included a dashboard, seed script, Docker, and tests
   - Confirmed YOLO integration was optional and should not block the end-to-end system
3. Selected an implementation plan:
   - Build the core API and SSE flow first
   - Add a lightweight dashboard to demonstrate real-time behavior
   - Add test coverage, local run instructions, and Docker support
4. Implemented the project on local disk in `D:\Projects\traffic-incident-api`
5. Ran local verification and fixed issues discovered during test execution
6. Extended the project into a training-enabled version:
   - Added downloaders for official MIO-TCD, RDD2022, and TRANCOS archives
   - Added dataset conversion scripts for MIO-TCD and RDD2022
   - Added YOLO training commands and video-to-API inference utilities
   - Routed all large caches, datasets, runs, and snapshots to `D:\Datasets\traffic-incident`
   - Verified a non-dry-run RDD2022 video inference path that inserted two `DEBRIS` events through the API

## Key design decisions

- Used SSE instead of WebSockets because the requirement is one-way push from server to dashboard.
- Used SQLite for a portable evaluation environment and simple Docker volume persistence.
- Kept explicit status workflow rules, but added rollback paths after UI review so operators can recover from accidental clicks.
- Returned a unified `{ success, data }` envelope and `{ success, error }` for failures.
- Chose MIO-TCD as the trainable vehicle dataset because it is official and directly suitable for stopped-vehicle and congestion heuristics.
- Chose RDD2022 as the openly available road-hazard proxy dataset and mapped its outputs to the platform's `DEBRIS` event type.
- Kept all ML-heavy assets on `D:` to respect the limited free space on `C:`.

## Remaining work not included

- Authentication and authorization
- Production-grade deployment concerns such as rate limiting and observability
- Full end-to-end model training completion time depends on local download speed and GPU runtime budget
