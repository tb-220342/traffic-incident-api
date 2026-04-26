from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import cv2
import httpx

from yolo.config import MOTOR_VEHICLE_CLASSES, SNAPSHOT_ROOT, ensure_runtime_dirs


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def post_detected_incident(
    base_url: str,
    *,
    event_type: str,
    severity: str,
    confidence: float,
    camera_id: str,
    latitude: float,
    longitude: float,
    description: str | None = None,
    highway_id: str | None = None,
    image_url: str | None = None,
) -> dict:
    payload = {
        "source_event_id": f"{camera_id}:{event_type}:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%f')}:{uuid4().hex[:8]}",
        "event_type": event_type,
        "severity": severity,
        "description": description,
        "confidence": confidence,
        "camera_id": camera_id,
        "highway_id": highway_id,
        "latitude": latitude,
        "longitude": longitude,
        "image_url": image_url,
        "detected_at": utc_now_iso(),
        "extra_payload": {"source": "yolo.detector"},
    }

    response = httpx.post(f"{base_url}/events", json=payload, timeout=10.0)
    response.raise_for_status()
    return response.json()


def save_snapshot(frame, source_name: str, frame_index: int) -> Path:
    ensure_runtime_dirs()
    target_dir = SNAPSHOT_ROOT / source_name
    target_dir.mkdir(parents=True, exist_ok=True)
    output_path = target_dir / f"frame-{frame_index:06d}.jpg"
    cv2.imwrite(str(output_path), frame)
    return output_path


@dataclass
class TrackSample:
    frame_index: int
    center_x: float
    center_y: float


@dataclass
class TrackHistory:
    samples: deque[TrackSample] = field(default_factory=lambda: deque(maxlen=180))
    last_reported_frame: int = -10_000

    def add(self, sample: TrackSample) -> None:
        self.samples.append(sample)

    def mean_motion(self) -> float:
        if len(self.samples) < 2:
            return 0.0
        total = 0.0
        previous = self.samples[0]
        for current in list(self.samples)[1:]:
            total += ((current.center_x - previous.center_x) ** 2 + (current.center_y - previous.center_y) ** 2) ** 0.5
            previous = current
        return total / (len(self.samples) - 1)


def inside_roi(center_x: float, center_y: float, roi: tuple[float, float, float, float], frame_width: int, frame_height: int) -> bool:
    left = roi[0] * frame_width
    top = roi[1] * frame_height
    right = roi[2] * frame_width
    bottom = roi[3] * frame_height
    return left <= center_x <= right and top <= center_y <= bottom


def is_motor_vehicle(class_name: str) -> bool:
    return class_name in MOTOR_VEHICLE_CLASSES
