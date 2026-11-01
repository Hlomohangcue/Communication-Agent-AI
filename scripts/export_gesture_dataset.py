import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.core.settings import settings
from backend.services.gesture_dataset import (
    DatasetValidationError,
    GestureDatasetService,
    split_records_by_participant,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export validated gesture samples into participant-disjoint JSONL splits."
    )
    parser.add_argument("--input", type=Path, default=Path(settings.gesture_dataset_path))
    parser.add_argument("--output-dir", type=Path, default=Path("data/gesture_splits"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing train, validation, test and manifest files.",
    )
    args = parser.parse_args()

    dataset = GestureDatasetService(
        args.input,
        gesture_labels=settings.gesture_dataset_labels,
        dynamic_labels=settings.gesture_dataset_dynamic_labels,
    )
    try:
        records = dataset.read_records()
        splits = split_records_by_participant(records, seed=args.seed)
    except (DatasetValidationError, OSError) as exc:
        parser.error(str(exc))
    manifest_path = args.output_dir / "split_manifest.json"
    output_paths = {
        split: args.output_dir / f"{split}.jsonl"
        for split in ("train", "validation", "test")
    }
    existing = [path for path in [*output_paths.values(), manifest_path] if path.exists()]
    if existing and not args.overwrite:
        parser.error(
            "Output already exists; choose a new directory or pass --overwrite: "
            + ", ".join(str(path) for path in existing)
        )

    participant_splits = {
        split: sorted({record["participant_id"] for record in split_records})
        for split, split_records in splits.items()
    }
    for split, split_records in splits.items():
        output_paths[split].parent.mkdir(parents=True, exist_ok=True)
        output_paths[split].write_text(
            "".join(
                json.dumps(record, separators=(",", ":"), ensure_ascii=False) + "\n"
                for record in split_records
            ),
            encoding="utf-8",
        )
    manifest_path.write_text(
        json.dumps(
            {
                "dataset_version": 1,
                "seed": args.seed,
                "participant_ids": participant_splits,
                "record_counts": {
                    split: len(split_records) for split, split_records in splits.items()
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    for split, split_records in splits.items():
        print(
            f"{split}: {len(split_records)} records, "
            f"{len(participant_splits[split])} participants -> {output_paths[split]}"
        )
    print(f"Split manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
