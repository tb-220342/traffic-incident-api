from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path

from PIL import Image

from yolo.config import PREPARED_ROOT, RAW_ROOT, TRANCOS_CLASSES, ensure_runtime_dirs


SPLIT_MAP = {
    "training.txt": "train",
    "validation.txt": "val",
}


def hardlink_or_copy(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        return
    try:
        os.link(source, destination)
    except OSError:
        shutil.copy2(source, destination)


def discover_dataset_root(raw_root: Path) -> Path:
    candidate = raw_root / "trancos" / "TRANCOS_v3"
    if candidate.exists():
        return candidate
    candidate = raw_root / "TRANCOS_v3"
    if candidate.exists():
        return candidate
    raise FileNotFoundError("Unable to locate the extracted TRANCOS_v3 dataset.")


def normalized_box(width: int, height: int, center_x: float, center_y: float, box_size: int) -> tuple[float, float, float, float]:
    half = box_size / 2
    xmin = max(0.0, center_x - half)
    ymin = max(0.0, center_y - half)
    xmax = min(float(width), center_x + half)
    ymax = min(float(height), center_y + half)

    clipped_width = max(xmax - xmin, 1.0)
    clipped_height = max(ymax - ymin, 1.0)
    return (
        (xmin + clipped_width / 2) / width,
        (ymin + clipped_height / 2) / height,
        clipped_width / width,
        clipped_height / height,
    )


def read_points(annotation_path: Path) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for line in annotation_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        points.append((float(parts[0]), float(parts[1])))
    return points


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert the TRANCOS counting dataset into an approximate YOLO detection dataset.")
    parser.add_argument("--raw-root", default=str(RAW_ROOT), help="Dataset root used by the downloader.")
    parser.add_argument("--output-root", default=str(PREPARED_ROOT / "trancos"), help="Prepared YOLO dataset output root.")
    parser.add_argument(
        "--box-size-factor",
        type=float,
        default=0.03,
        help="Square box side as a fraction of the smaller image dimension.",
    )
    parser.add_argument("--min-box-px", type=int, default=18, help="Minimum point-derived bounding-box side length in pixels.")
    args = parser.parse_args()

    ensure_runtime_dirs()

    dataset_root = discover_dataset_root(Path(args.raw_root))
    output_root = Path(args.output_root)
    images_dir = dataset_root / "images"
    image_sets_dir = dataset_root / "image_sets"

    images_root = output_root / "images"
    labels_root = output_root / "labels"
    for split in ("train", "val"):
        (images_root / split).mkdir(parents=True, exist_ok=True)
        (labels_root / split).mkdir(parents=True, exist_ok=True)

    split_indexes: dict[str, list[str]] = {"train": [], "val": []}

    for split_file, split_name in SPLIT_MAP.items():
        split_path = image_sets_dir / split_file
        if not split_path.exists():
            raise FileNotFoundError(f"Expected split file at {split_path}")

        image_ids = [line.strip() for line in split_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        for image_id in image_ids:
            stem = Path(image_id).stem
            image_name = image_id if Path(image_id).suffix else f"{image_id}.jpg"
            image_path = images_dir / image_name
            annotation_path = images_dir / f"{stem}.txt"

            if not image_path.exists():
                raise FileNotFoundError(f"Unable to locate TRANCOS image {image_path}")
            if not annotation_path.exists():
                raise FileNotFoundError(f"Unable to locate TRANCOS point annotation {annotation_path}")

            with Image.open(image_path) as image:
                width, height = image.size

            points = read_points(annotation_path)
            if not points:
                continue

            box_size = max(args.min_box_px, round(min(width, height) * args.box_size_factor))
            lines = []
            seen = set()
            for center_x, center_y in points:
                x_center, y_center, box_width, box_height = normalized_box(width, height, center_x, center_y, box_size)
                line = f"0 {x_center:.6f} {y_center:.6f} {box_width:.6f} {box_height:.6f}"
                if line in seen:
                    continue
                seen.add(line)
                lines.append(line)

            destination_image = images_root / split_name / image_path.name
            destination_label = labels_root / split_name / f"{image_path.stem}.txt"
            hardlink_or_copy(image_path, destination_image)
            destination_label.write_text("\n".join(lines) + "\n", encoding="utf-8")
            split_indexes[split_name].append(str(destination_image.resolve()))

    (output_root / "train.txt").write_text("\n".join(split_indexes["train"]) + "\n", encoding="utf-8")
    (output_root / "val.txt").write_text("\n".join(split_indexes["val"]) + "\n", encoding="utf-8")
    (output_root / "data.yaml").write_text(
        "\n".join(
            [
                f"path: {output_root.as_posix()}",
                "train: train.txt",
                "val: val.txt",
                "names:",
                *[f"  {index}: {name}" for index, name in enumerate(TRANCOS_CLASSES)],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Prepared TRANCOS dataset at {output_root}")
    print(f"train images: {len(split_indexes['train'])}")
    print(f"val images: {len(split_indexes['val'])}")


if __name__ == "__main__":
    main()
