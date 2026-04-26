from __future__ import annotations

import argparse
from collections import defaultdict, deque
from pathlib import Path

import cv2

from yolo.detector import TrackHistory, TrackSample, inside_roi, is_motor_vehicle, post_detected_incident, save_snapshot


def parse_roi(raw: str) -> tuple[float, float, float, float]:
    values = [float(part) for part in raw.split(",")]
    if len(values) != 4:
        raise ValueError("ROI must contain four comma-separated values: x1,y1,x2,y2")
    return values[0], values[1], values[2], values[3]


def severity_from_duration(seconds: float) -> str:
    if seconds >= 12:
        return "CRITICAL"
    if seconds >= 8:
        return "HIGH"
    if seconds >= 4:
        return "MEDIUM"
    return "LOW"


def damage_severity(confidence: float) -> str:
    if confidence >= 0.9:
        return "HIGH"
    if confidence >= 0.8:
        return "MEDIUM"
    return "LOW"


def build_writer(output_path: str | None, fps: float, frame_width: int, frame_height: int):
    if not output_path:
        return None

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(
        str(path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (frame_width, frame_height),
    )
    if not writer.isOpened():
        raise RuntimeError(f"Could not open annotated video writer: {path}")
    return writer


def report_incident(args, **payload) -> None:
    if args.dry_run:
        print(
            "[dry-run] would report "
            f"{payload['event_type']} {payload['severity']} "
            f"confidence={payload['confidence']:.2f} camera={payload['camera_id']}"
        )
        return

    post_detected_incident(args.base_url, **payload)


def run_vehicle_monitor(args) -> None:
    from ultralytics import YOLO

    model = YOLO(args.weights)
    frame_index = 0
    roi = parse_roi(args.roi)
    histories: dict[int, TrackHistory] = defaultdict(TrackHistory)
    congestion_window: deque[tuple[int, float]] = deque(maxlen=90)
    last_congestion_frame = -10_000

    cap = cv2.VideoCapture(args.source)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    min_stop_frames = int(args.stop_seconds * fps)
    cooldown_frames = int(args.cooldown_seconds * fps)
    writer = None

    stream = model.track(
        source=args.source,
        stream=True,
        tracker="bytetrack.yaml",
        conf=args.confidence,
        persist=True,
        verbose=False,
    )

    for result in stream:
        frame = result.orig_img
        if frame is None:
            frame = result.plot()

        frame_height, frame_width = frame.shape[:2]
        if writer is None:
            writer = build_writer(args.annotated_output, fps, frame_width, frame_height)

        if writer is not None:
            writer.write(result.plot())

        active_vehicle_speeds = []
        active_vehicle_count = 0

        if result.boxes is not None and result.boxes.id is not None:
            ids = result.boxes.id.int().tolist()
            classes = result.boxes.cls.int().tolist()
            confidences = result.boxes.conf.tolist()
            boxes = result.boxes.xyxy.tolist()

            for track_id, class_id, confidence, box in zip(ids, classes, confidences, boxes):
                class_name = result.names[class_id]
                if not is_motor_vehicle(class_name):
                    continue

                xmin, ymin, xmax, ymax = box
                center_x = (xmin + xmax) / 2
                center_y = (ymin + ymax) / 2
                if not inside_roi(center_x, center_y, roi, frame_width, frame_height):
                    continue

                active_vehicle_count += 1
                history = histories[track_id]
                history.add(TrackSample(frame_index=frame_index, center_x=center_x, center_y=center_y))
                active_vehicle_speeds.append(history.mean_motion())

                if len(history.samples) >= min_stop_frames:
                    dwell_frames = history.samples[-1].frame_index - history.samples[0].frame_index + 1
                    if dwell_frames >= min_stop_frames and history.mean_motion() <= args.stop_motion_px:
                        if frame_index - history.last_reported_frame >= cooldown_frames:
                            snapshot = save_snapshot(frame, Path(args.source).stem, frame_index)
                            seconds_stopped = dwell_frames / fps
                            report_incident(
                                args,
                                event_type="STOPPED_VEHICLE",
                                severity=severity_from_duration(seconds_stopped),
                                confidence=float(confidence),
                                camera_id=args.camera_id,
                                highway_id=args.highway_id,
                                latitude=args.latitude,
                                longitude=args.longitude,
                                description=f"{class_name} stopped in ROI for {seconds_stopped:.1f}s",
                                image_url=str(snapshot),
                            )
                            history.last_reported_frame = frame_index
                            print(f"[frame {frame_index}] reported STOPPED_VEHICLE for track {track_id}")

        mean_speed = sum(active_vehicle_speeds) / len(active_vehicle_speeds) if active_vehicle_speeds else 0.0
        congestion_window.append((active_vehicle_count, mean_speed))
        if len(congestion_window) == congestion_window.maxlen:
            avg_count = sum(item[0] for item in congestion_window) / len(congestion_window)
            avg_speed = sum(item[1] for item in congestion_window) / len(congestion_window)
            if avg_count >= args.congestion_vehicle_threshold and avg_speed <= args.congestion_motion_px:
                if frame_index - last_congestion_frame >= cooldown_frames:
                    snapshot = save_snapshot(frame, Path(args.source).stem, frame_index)
                    confidence = min(0.99, 0.5 + avg_count / (args.congestion_vehicle_threshold * 2))
                    report_incident(
                        args,
                        event_type="CONGESTION",
                        severity="HIGH" if avg_count >= args.congestion_vehicle_threshold * 1.5 else "MEDIUM",
                        confidence=confidence,
                        camera_id=args.camera_id,
                        highway_id=args.highway_id,
                        latitude=args.latitude,
                        longitude=args.longitude,
                        description=f"Persistent congestion in ROI with avg_count={avg_count:.1f} avg_motion={avg_speed:.2f}px",
                        image_url=str(snapshot),
                    )
                    last_congestion_frame = frame_index
                    print(f"[frame {frame_index}] reported CONGESTION")

        frame_index += 1

    cap.release()
    if writer is not None:
        writer.release()


def run_damage_monitor(args) -> None:
    from ultralytics import YOLO

    model = YOLO(args.weights)
    cap = cv2.VideoCapture(args.source)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cooldown_frames = max(int(args.cooldown_seconds * fps), 1)
    last_reported_frame = -cooldown_frames
    frame_index = 0
    writer = None
    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if writer is None:
            frame_height, frame_width = frame.shape[:2]
            writer = build_writer(args.annotated_output, fps, frame_width, frame_height)

        if frame_index % args.frame_stride != 0:
            if writer is not None:
                writer.write(frame)
            frame_index += 1
            continue

        results = model.predict(frame, conf=args.confidence, verbose=False)
        result = results[0]
        if writer is not None:
            writer.write(result.plot())

        if result.boxes is not None and len(result.boxes) > 0:
            top_confidence = max(result.boxes.conf.tolist())
            labels = [result.names[class_id] for class_id in result.boxes.cls.int().tolist()]
            unique_labels = ",".join(sorted(set(labels)))
            if frame_index - last_reported_frame >= cooldown_frames:
                snapshot = save_snapshot(frame, Path(args.source).stem, frame_index)
                report_incident(
                    args,
                    event_type="DEBRIS",
                    severity=damage_severity(top_confidence),
                    confidence=float(top_confidence),
                    camera_id=args.camera_id,
                    highway_id=args.highway_id,
                    latitude=args.latitude,
                    longitude=args.longitude,
                    description=f"Road anomaly detected ({unique_labels})",
                    image_url=str(snapshot),
                )
                last_reported_frame = frame_index
                print(f"[frame {frame_index}] reported DEBRIS with labels {unique_labels}")

        frame_index += 1

    cap.release()
    if writer is not None:
        writer.release()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a trained YOLO model on video and post incidents back to the API.")
    parser.add_argument("--mode", choices=["vehicle", "damage"], required=True, help="Inference mode.")
    parser.add_argument("--weights", required=True, help="Path to the trained YOLO weights file.")
    parser.add_argument("--source", required=True, help="Video or stream source path.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Traffic incident API base URL.")
    parser.add_argument("--camera-id", default="CAM-YOLO-001", help="Camera identifier to send with generated events.")
    parser.add_argument("--highway-id", default="E1", help="Highway identifier to send with generated events.")
    parser.add_argument("--latitude", type=float, default=35.6804, help="Latitude for generated events.")
    parser.add_argument("--longitude", type=float, default=139.7690, help="Longitude for generated events.")
    parser.add_argument("--confidence", type=float, default=0.35, help="Minimum prediction confidence.")
    parser.add_argument("--roi", default="0.1,0.25,0.9,0.9", help="Normalized ROI as x1,y1,x2,y2 for vehicle mode.")
    parser.add_argument("--stop-seconds", type=float, default=4.0, help="Seconds a track must remain nearly static before reporting STOPPED_VEHICLE.")
    parser.add_argument("--stop-motion-px", type=float, default=4.0, help="Average pixel movement threshold for a stopped track.")
    parser.add_argument("--congestion-vehicle-threshold", type=float, default=8.0, help="Average vehicle count threshold for congestion reports.")
    parser.add_argument("--congestion-motion-px", type=float, default=7.0, help="Average motion threshold for congestion reports.")
    parser.add_argument("--cooldown-seconds", type=float, default=15.0, help="Cooldown between repeated reports of the same event.")
    parser.add_argument("--frame-stride", type=int, default=10, help="How many frames to skip between damage detections.")
    parser.add_argument("--annotated-output", default=None, help="Optional path for an MP4 video with YOLO boxes drawn.")
    parser.add_argument("--dry-run", action="store_true", help="Run detection without posting incidents to the API.")
    args = parser.parse_args()

    if args.mode == "vehicle":
        run_vehicle_monitor(args)
    else:
        run_damage_monitor(args)


if __name__ == "__main__":
    main()
