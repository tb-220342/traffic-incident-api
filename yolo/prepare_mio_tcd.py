from __future__ import annotations

import argparse
import csv
import hashlib
import os
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image

from yolo.config import MIO_CLASSES, PREPARED_ROOT, RAW_ROOT, ensure_runtime_dirs


def normalized_box(width: int, height: int, xmin: float, ymin: float, xmax: float, ymax: float) -> tuple[float, float, float, float]:
    box_width = max(xmax - xmin, 1.0)
    box_height = max(ymax - ymin, 1.0)
    center_x = xmin + box_width / 2
    center_y = ymin + box_height / 2
    return (
        center_x / width,
        center_y / height,
        box_width / width,
        box_height / height,
    )


def stable_split(name: str, val_ratio: float) -> str:
    value = int(hashlib.sha1(name.encode("utf-8")).hexdigest(), 16) % 10_000
    return "val" if value < int(val_ratio * 10_000) else "train"


def hardlink_or_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def discover_dataset_root(raw_root: Path) -> tuple[Path, Path]:
    candidate = raw_root / "mio-localization"
    if candidate.exists():
        raw_root = candidate

    gt_train = next(raw_root.rglob("gt_train.csv"), None)
    if gt_train is None:
        raise FileNotFoundError("Unable to locate gt_train.csv inside the extracted MIO dataset.")

    train_dir = next((path for path in gt_train.parent.rglob("train") if path.is_dir()), None)
    if train_dir is None:
        raise FileNotFoundError("Unable to locate the train image directory inside the extracted MIO dataset.")

    return gt_train, train_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert the MIO-TCD localization dataset to YOLO format.")
    parser.add_argument("--raw-root", default=str(RAW_ROOT), help="Dataset root used by the downloader.")
    parser.add_argument("--output-root", default=str(PREPARED_ROOT / "mio-localization"), help="Prepared YOLO dataset output root.")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio.")
    args = parser.parse_args()

    ensure_runtime_dirs()

    raw_root = Path(args.raw_root)
    output_root = Path(args.output_root)
    gt_train, train_dir = discover_dataset_root(raw_root)

    images_root = output_root / "images"
    labels_root = output_root / "labels"
    for split in ("train", "val"):
        (images_root / split).mkdir(parents=True, exist_ok=True)
        (labels_root / split).mkdir(parents=True, exist_ok=True)

    annotations: dict[str, list[tuple[str, float, float, float, float]]] = defaultdict(list)
    with gt_train.open("r", encoding="utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            image_id, label, xmin, ymin, xmax, ymax = row
            if label not in MIO_CLASSES:
                continue
            annotations[image_id].append((label, float(xmin), float(ymin), float(xmax), float(ymax)))

    train_index: list[str] = []
    val_index: list[str] = []

    for image_id, boxes in annotations.items():
        image_path = train_dir / f"{image_id}.jpg"
        if not image_path.exists():
            image_path = train_dir / f"{image_id}.jpeg"
        if not image_path.exists():
            image_path = train_dir / f"{image_id}.png"
        if not image_path.exists():
            raise FileNotFoundError(f"Unable to locate image for {image_id}")

        split = stable_split(image_id, args.val_ratio)
        destination_image = images_root / split / image_path.name
        destination_label = labels_root / split / f"{image_path.stem}.txt"

        with Image.open(image_path) as image:
            width, height = image.size

        lines = []
        for label, xmin, ymin, xmax, ymax in boxes:
            class_id = MIO_CLASSES.index(label)
            x_center, y_center, box_width, box_height = normalized_box(width, height, xmin, ymin, xmax, ymax)
            lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}")

        hardlink_or_copy(image_path, destination_image)
        destination_label.write_text("\n".join(lines) + "\n", encoding="utf-8")

        image_record = str(destination_image.resolve())
        if split == "train":
            train_index.append(image_record)
        else:
            val_index.append(image_record)

    (output_root / "train.txt").write_text("\n".join(train_index) + "\n", encoding="utf-8")
    (output_root / "val.txt").write_text("\n".join(val_index) + "\n", encoding="utf-8")
    (output_root / "data.yaml").write_text(
        "\n".join(
            [
                f"path: {output_root.as_posix()}",
                "train: train.txt",
                "val: val.txt",
                "names:",
                *[f"  {index}: {name}" for index, name in enumerate(MIO_CLASSES)],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Prepared MIO dataset at {output_root}")
    print(f"train images: {len(train_index)}")
    print(f"val images: {len(val_index)}")


if __name__ == "__main__":
    main()
