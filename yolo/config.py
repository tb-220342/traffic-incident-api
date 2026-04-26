from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

DATASETS_ROOT = Path(os.environ.get("TRAFFIC_DATASETS_ROOT", r"D:\Datasets\traffic-incident"))
CACHE_ROOT = Path(os.environ.get("TRAFFIC_CACHE_ROOT", str(DATASETS_ROOT / "cache")))
RUNS_ROOT = Path(os.environ.get("TRAFFIC_RUNS_ROOT", str(DATASETS_ROOT / "runs")))

RAW_ROOT = DATASETS_ROOT / "raw"
PREPARED_ROOT = DATASETS_ROOT / "prepared"
SNAPSHOT_ROOT = DATASETS_ROOT / "snapshots"

MIO_CLASSES = [
    "articulated_truck",
    "bicycle",
    "bus",
    "car",
    "motorcycle",
    "motorized_vehicle",
    "non-motorized_vehicle",
    "pedestrian",
    "pickup_truck",
    "single_unit_truck",
    "work_van",
]

RDD2022_CLASSES = ["D00", "D10", "D20", "D40"]
TRANCOS_CLASSES = ["vehicle"]

MOTOR_VEHICLE_CLASSES = {
    "articulated_truck",
    "bus",
    "car",
    "motorcycle",
    "motorized_vehicle",
    "pickup_truck",
    "single_unit_truck",
    "work_van",
}


@dataclass(frozen=True)
class DownloadSpec:
    key: str
    url: str
    archive_name: str
    extract_dir: str
    description: str


DOWNLOAD_SPECS = {
    "mio-localization": DownloadSpec(
        key="mio-localization",
        url="https://tcd.miovision.com/static/dataset/MIO-TCD-Localization.tar",
        archive_name="MIO-TCD-Localization.tar",
        extract_dir="mio-localization",
        description="Official MIO-TCD localization dataset for training the vehicle detector.",
    ),
    "rdd2022": DownloadSpec(
        key="rdd2022",
        url="https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/RDD2022.zip",
        archive_name="RDD2022.zip",
        extract_dir="rdd2022",
        description="Official RDD2022 road damage dataset from the CRDDC challenge.",
    ),
    "trancos": DownloadSpec(
        key="trancos",
        url="https://universidaddealcala-my.sharepoint.com/:u:/g/personal/gram_uah_es/Eank6osXQgxEqa-1bb0nVsoBc3xO4XDwENc_g0nc6t58BA?Download=1",
        archive_name="TRANCOS_v3.tar.gz",
        extract_dir="trancos",
        description="Official TRANCOS vehicle counting dataset used to calibrate congestion thresholds.",
    ),
}


@dataclass(frozen=True)
class TrainProfile:
    key: str
    data_yaml: Path
    model: str
    epochs: int
    imgsz: int
    batch: int
    project_name: str
    description: str


def get_train_profiles() -> dict[str, TrainProfile]:
    return {
        "mio-localization": TrainProfile(
            key="mio-localization",
            data_yaml=PREPARED_ROOT / "mio-localization" / "data.yaml",
            model="yolov8n.pt",
            epochs=50,
            imgsz=640,
            batch=16,
            project_name="mio-localization",
            description="Train a vehicle localization model used for stopped-vehicle and congestion event generation.",
        ),
        "rdd2022": TrainProfile(
            key="rdd2022",
            data_yaml=PREPARED_ROOT / "rdd2022" / "data.yaml",
            model="yolov8n.pt",
            epochs=60,
            imgsz=960,
            batch=8,
            project_name="rdd2022",
            description="Train a road-anomaly detector that can be mapped to debris-style roadway hazard events.",
        ),
        "trancos": TrainProfile(
            key="trancos",
            data_yaml=PREPARED_ROOT / "trancos" / "data.yaml",
            model="yolov8n.pt",
            epochs=40,
            imgsz=640,
            batch=16,
            project_name="trancos",
            description="Train a point-to-box vehicle detector used to calibrate congestion density on TRANCOS frames.",
        ),
    }


def ensure_runtime_dirs() -> None:
    for path in (DATASETS_ROOT, CACHE_ROOT, RUNS_ROOT, RAW_ROOT, PREPARED_ROOT, SNAPSHOT_ROOT):
        path.mkdir(parents=True, exist_ok=True)
