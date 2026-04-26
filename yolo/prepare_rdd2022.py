from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from PIL import Image

from yolo.config import PREPARED_ROOT, RAW_ROOT, RDD2022_CLASSES, ensure_runtime_dirs


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


def find_image_for_xml(xml_path: Path) -> Path | None:
    stem = xml_path.stem
    parent = xml_path.parent
    candidates = [
        parent / f"{stem}.jpg",
        parent / f"{stem}.JPG",
        parent / f"{stem}.png",
        parent / f"{stem}.PNG",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    for ancestor in xml_path.parents:
        nearby_images = list(ancestor.rglob(f"{stem}.*"))
        for candidate in nearby_images:
            if candidate.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                return candidate
    return None


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


def extract_objects(xml_path: Path) -> tuple[list[tuple[str, float, float, float, float]], tuple[int, int]]:
    tree = ET.parse(xml_path)
    root = tree.getroot()
    size_node = root.find("size")
    width = int(size_node.findtext("width", "0")) if size_node is not None else 0
    height = int(size_node.findtext("height", "0")) if size_node is not None else 0

    objects: list[tuple[str, float, float, float, float]] = []
    for object_node in root.findall("object"):
        label = object_node.findtext("name", default="").strip()
        if label not in RDD2022_CLASSES:
            continue
        bbox = object_node.find("bndbox")
        if bbox is None:
            continue
        xmin = float(bbox.findtext("xmin", "0"))
        ymin = float(bbox.findtext("ymin", "0"))
        xmax = float(bbox.findtext("xmax", "0"))
        ymax = float(bbox.findtext("ymax", "0"))
        objects.append((label, xmin, ymin, xmax, ymax))

    return objects, (width, height)


def extract_nested_archives(dataset_root: Path) -> Path:
    extract_root = dataset_root / "_expanded"
    extract_root.mkdir(parents=True, exist_ok=True)

    for archive_path in dataset_root.rglob("*.zip"):
        target_dir = extract_root / archive_path.stem
        marker = target_dir / ".done"
        if marker.exists():
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(target_dir)
        marker.write_text("ok", encoding="utf-8")

    return extract_root


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert the official RDD2022 dataset to YOLO format.")
    parser.add_argument("--raw-root", default=str(RAW_ROOT), help="Dataset root used by the downloader.")
    parser.add_argument("--output-root", default=str(PREPARED_ROOT / "rdd2022"), help="Prepared YOLO dataset output root.")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio.")
    args = parser.parse_args()

    ensure_runtime_dirs()
    raw_root = Path(args.raw_root)
    output_root = Path(args.output_root)
    dataset_root = raw_root / "rdd2022" if (raw_root / "rdd2022").exists() else raw_root

    xml_files = sorted(dataset_root.rglob("*.xml"))
    if not xml_files:
        expanded_root = extract_nested_archives(dataset_root)
        xml_files = sorted(expanded_root.rglob("*.xml"))
    if not xml_files:
        raise FileNotFoundError("Unable to locate any XML annotations inside the extracted RDD2022 dataset.")

    images_root = output_root / "images"
    labels_root = output_root / "labels"
    for split in ("train", "val"):
        (images_root / split).mkdir(parents=True, exist_ok=True)
        (labels_root / split).mkdir(parents=True, exist_ok=True)

    train_index: list[str] = []
    val_index: list[str] = []

    for xml_path in xml_files:
        objects, size = extract_objects(xml_path)
        if not objects:
            continue

        image_path = find_image_for_xml(xml_path)
        if image_path is None:
            continue

        width, height = size
        if width <= 0 or height <= 0:
            with Image.open(image_path) as image:
                width, height = image.size

        split = stable_split(str(xml_path.relative_to(dataset_root)), args.val_ratio)
        destination_image = images_root / split / image_path.name
        destination_label = labels_root / split / f"{image_path.stem}.txt"

        lines = []
        for label, xmin, ymin, xmax, ymax in objects:
            class_id = RDD2022_CLASSES.index(label)
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
                *[f"  {index}: {name}" for index, name in enumerate(RDD2022_CLASSES)],
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Prepared RDD2022 dataset at {output_root}")
    print(f"train images: {len(train_index)}")
    print(f"val images: {len(val_index)}")


if __name__ == "__main__":
    main()
