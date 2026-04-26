from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone

from yolo.config import CACHE_ROOT, RUNS_ROOT, ensure_runtime_dirs, get_train_profiles


def main() -> None:
    parser = argparse.ArgumentParser(description="Train a YOLO model for the traffic incident monitoring project.")
    parser.add_argument("--profile", choices=sorted(get_train_profiles().keys()), required=True, help="Training profile to run.")
    parser.add_argument("--model", default=None, help="Override the default pretrained starting checkpoint.")
    parser.add_argument("--resume-from", default=None, help="Resume training from a previous run checkpoint such as last.pt.")
    parser.add_argument("--epochs", type=int, default=None, help="Override the default epoch count.")
    parser.add_argument("--imgsz", type=int, default=None, help="Override the default training image size.")
    parser.add_argument("--batch", type=int, default=None, help="Override the default batch size.")
    parser.add_argument("--device", default="0", help="CUDA device id or cpu.")
    parser.add_argument("--workers", type=int, default=4, help="Number of dataloader workers.")
    parser.add_argument("--name", default=None, help="Override the run name.")
    parser.add_argument("--fraction", type=float, default=1.0, help="Fraction of the dataset to use for a smoke run.")
    parser.add_argument("--save-period", type=int, default=-1, help="Save intermediate checkpoints every N epochs.")
    args = parser.parse_args()

    ensure_runtime_dirs()

    os.environ.setdefault("TORCH_HOME", str(CACHE_ROOT / "torch"))
    os.environ.setdefault("ULTRALYTICS_CACHE_DIR", str(CACHE_ROOT / "ultralytics"))

    profile = get_train_profiles()[args.profile]
    model_name = args.resume_from or args.model or profile.model
    run_name = args.name or datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    if not profile.data_yaml.exists():
        raise FileNotFoundError(
            f"Dataset YAML not found at {profile.data_yaml}. Run the matching prepare script before training."
        )

    from ultralytics import YOLO

    project_dir = RUNS_ROOT / profile.project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "profile": profile.key,
        "description": profile.description,
        "data_yaml": str(profile.data_yaml),
        "model": model_name,
        "epochs": args.epochs or profile.epochs,
        "imgsz": args.imgsz or profile.imgsz,
        "batch": args.batch or profile.batch,
        "device": args.device,
        "workers": args.workers,
        "fraction": args.fraction,
        "resume_from": args.resume_from,
        "save_period": args.save_period,
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    metadata_path = project_dir / f"{run_name}.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Training metadata written to {metadata_path}")

    model = YOLO(model_name)
    model.train(
        data=str(profile.data_yaml),
        epochs=args.epochs or profile.epochs,
        imgsz=args.imgsz or profile.imgsz,
        batch=args.batch or profile.batch,
        device=args.device,
        workers=args.workers,
        fraction=args.fraction,
        project=str(project_dir),
        name=run_name,
        exist_ok=True,
        pretrained=True,
        verbose=True,
        resume=bool(args.resume_from),
        save_period=args.save_period,
    )

    print(f"Training finished. Results saved under {project_dir / run_name}")


if __name__ == "__main__":
    main()
