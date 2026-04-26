YOLO video test set
===================

Public repository note:
This folder intentionally contains documentation only. The actual MP4 clips, annotated MP4 outputs, and snapshot images are dataset-derived artifacts and are not committed to the public GitHub repository.

Local artifact location:
D:\Datasets\traffic-incident\yolovideotest

Expected local input clips:
- mio_vehicle_short.mp4
  Source: generated from labeled MIO-TCD localization validation images.
  Purpose: vehicle detector / tracking demo.

- rdd_damage_short.mp4
  Source: generated from labeled RDD2022 validation images.
  Purpose: road anomaly / debris detector demo.

Expected local annotated outputs:
- mio_vehicle_short.boxes.mp4
- rdd_damage_short.boxes.mp4

Verified API write:
- On 2026-04-26, rdd_damage_short.mp4 was run without --dry-run.
- It inserted two DEBRIS events through POST /events with camera_id CAM-YOLO-VIDEO-RDD.
- The demo database keeps those two API events, but the snapshot images are local-only and excluded from public release.

Important note:
These are short slideshow-style clips created from existing dataset images, not original continuous road videos.
That is useful for a demo because it exposes model quality issues clearly:
- vehicle tracking is not reliable on image-sequence clips because frames are not temporally continuous
- RDD damage detection can show low-confidence boxes, missed defects, or boxes that do not align perfectly

Dry-run commands, no API writes:

powershell -ExecutionPolicy Bypass -Command "cd D:\Projects\traffic-incident-api; .\.venv\Scripts\python.exe -m yolo.infer_video --mode vehicle --weights D:\Datasets\traffic-incident\runs\mio-localization\mio-stage2-20260421-234643\weights\best.pt --source D:\Datasets\traffic-incident\yolovideotest\mio_vehicle_short.mp4 --base-url http://127.0.0.1:8000 --camera-id CAM-YOLO-VIDEO-MIO --highway-id E1 --confidence 0.25 --stop-seconds 1 --cooldown-seconds 5 --annotated-output D:\Datasets\traffic-incident\yolovideotest\mio_vehicle_short.boxes.mp4 --dry-run"

powershell -ExecutionPolicy Bypass -Command "cd D:\Projects\traffic-incident-api; .\.venv\Scripts\python.exe -m yolo.infer_video --mode damage --weights D:\Datasets\traffic-incident\runs\rdd2022\rdd-stage2-20260421-234643\weights\best.pt --source D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.mp4 --base-url http://127.0.0.1:8000 --camera-id CAM-YOLO-VIDEO-RDD --highway-id E1 --confidence 0.25 --frame-stride 1 --cooldown-seconds 5 --annotated-output D:\Datasets\traffic-incident\yolovideotest\rdd_damage_short.boxes.mp4 --dry-run"

To post generated incidents to the API, remove --dry-run.
