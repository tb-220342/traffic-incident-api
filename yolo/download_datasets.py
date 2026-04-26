from __future__ import annotations

import argparse
import tarfile
import zipfile
from pathlib import Path

import httpx

from yolo.config import CACHE_ROOT, DOWNLOAD_SPECS, RAW_ROOT, ensure_runtime_dirs

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
}


def stream_download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with httpx.Client(follow_redirects=True, timeout=None, headers=DEFAULT_HEADERS) as client:
        with client.stream("GET", url) as response:
            response.raise_for_status()
            total = int(response.headers.get("Content-Length", "0"))
            downloaded = 0
            last_percent = -1
            with destination.open("wb") as file:
                for chunk in response.iter_bytes():
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total:
                        progress = downloaded / total * 100
                        percent_bucket = int(progress)
                        if percent_bucket != last_percent or downloaded == total:
                            print(f"\rDownloading {destination.name}: {progress:6.2f}%", end="", flush=True)
                            last_percent = percent_bucket
            if total:
                print()


def extract_archive(archive_path: Path, extract_dir: Path) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)
    if archive_path.suffix == ".zip":
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(extract_dir)
        return

    if archive_path.suffix == ".tar" or archive_path.suffixes[-2:] == [".tar", ".gz"]:
        mode = "r:gz" if archive_path.suffixes[-2:] == [".tar", ".gz"] else "r:"
        with tarfile.open(archive_path, mode) as archive:
            archive.extractall(extract_dir)
        return

    raise ValueError(f"Unsupported archive format: {archive_path.name}")


def download_dataset(key: str, extract: bool) -> None:
    spec = DOWNLOAD_SPECS[key]
    ensure_runtime_dirs()

    archive_path = RAW_ROOT / spec.archive_name
    extract_dir = RAW_ROOT / spec.extract_dir
    marker = extract_dir / ".download_complete"

    print(f"[{key}] {spec.description}")
    print(f"[{key}] archive: {archive_path}")
    print(f"[{key}] extract: {extract_dir}")

    if not archive_path.exists():
        stream_download(spec.url, archive_path)
    else:
        print(f"[{key}] archive already exists, skipping download")

    if extract:
        if not marker.exists():
            extract_archive(archive_path, extract_dir)
            marker.write_text("ok", encoding="utf-8")
            print(f"[{key}] extraction complete")
        else:
            print(f"[{key}] extraction already completed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download official datasets for the traffic-incident YOLO pipeline.")
    parser.add_argument(
        "--datasets",
        nargs="+",
        default=["mio-localization", "rdd2022", "trancos"],
        choices=sorted(DOWNLOAD_SPECS.keys()),
        help="One or more dataset keys to download.",
    )
    parser.add_argument(
        "--no-extract",
        action="store_true",
        help="Download archives only and skip extraction.",
    )
    parser.add_argument(
        "--show-paths",
        action="store_true",
        help="Print resolved cache and raw dataset locations before downloading.",
    )
    args = parser.parse_args()

    if args.show_paths:
        print(f"CACHE_ROOT={CACHE_ROOT}")
        print(f"RAW_ROOT={RAW_ROOT}")

    failures: list[tuple[str, str]] = []
    for key in args.datasets:
        try:
            download_dataset(key, extract=not args.no_extract)
        except Exception as exc:  # noqa: BLE001
            failures.append((key, str(exc)))
            print(f"[{key}] failed: {exc}")

    if failures:
        raise SystemExit(
            "Dataset download completed with failures: "
            + "; ".join(f"{key}: {message}" for key, message in failures)
        )


if __name__ == "__main__":
    main()
