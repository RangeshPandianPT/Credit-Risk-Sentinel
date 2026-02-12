import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

import pandas as pd


def pick_time_column(app_path: Path, candidates: List[str]) -> str:
    # Read only the header to avoid loading the full dataset.
    columns = pd.read_csv(app_path, nrows=0).columns
    for name in candidates:
        if name in columns:
            return name
    raise ValueError(
        "No suitable time column found. Provide --time-column explicitly."
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 2 training wrapper that enforces leakage checks."
    )
    parser.add_argument(
        "--application-train",
        type=Path,
        default=Path("application_train.csv"),
        help="Path to application_train.csv",
    )
    parser.add_argument(
        "--phase1-features",
        type=Path,
        default=Path("phase1_behavioral_features.csv"),
        help="Path to Phase 1 feature CSV",
    )
    parser.add_argument(
        "--time-column",
        type=str,
        default=None,
        help="Time column used for temporal split (auto-picks if omitted)",
    )
    parser.add_argument(
        "--time-cutoff",
        type=float,
        required=True,
        help="Cutoff for temporal split (train <= cutoff)",
    )
    parser.add_argument(
        "--leakage-report",
        type=Path,
        required=True,
        help="Leakage report CSV from Phase 1",
    )
    parser.add_argument(
        "--model-output",
        type=Path,
        default=Path("artifacts/xgb_model.json"),
        help="Output path for the trained model artifact",
    )
    parser.add_argument(
        "--feature-output",
        type=Path,
        default=Path("artifacts/feature_list.csv"),
        help="Output path for the feature list",
    )
    parser.add_argument("--n-splits", type=int, default=5)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    time_column = args.time_column
    if time_column is None:
        time_column = pick_time_column(
            args.application_train,
            [
                "DAYS_ID_PUBLISH",
                "DAYS_REGISTRATION",
                "DAYS_LAST_PHONE_CHANGE",
                "DAYS_EMPLOYED",
                "DAYS_BIRTH",
            ],
        )
        print(f"Auto-selected time column: {time_column}")

    command = [
        sys.executable,
        str(Path("phase2_training_pipeline.py")),
        "--application-train",
        str(args.application_train),
        "--phase1-features",
        str(args.phase1_features),
        "--time-column",
        time_column,
        "--time-cutoff",
        str(args.time_cutoff),
        "--leakage-report",
        str(args.leakage_report),
        "--model-output",
        str(args.model_output),
        "--feature-output",
        str(args.feature_output),
        "--n-splits",
        str(args.n_splits),
        "--random-state",
        str(args.random_state),
    ]

    result = subprocess.run(command, check=False)
    return int(result.returncode)


if __name__ == "__main__":
    raise SystemExit(main())
