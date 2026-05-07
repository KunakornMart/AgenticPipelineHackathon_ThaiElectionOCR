"""
Validate submission format for Thai Election OCR Challenge.

Official output format:
id,votes
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = ["id", "votes"]


def validate_submission(path: str | Path, template_path: str | Path | None = None) -> None:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Submission file not found: {path}")

    sub = pd.read_csv(path, dtype={"id": str, "votes": str})

    if list(sub.columns) != REQUIRED_COLUMNS:
        raise ValueError(f"Invalid columns. Expected {REQUIRED_COLUMNS}, got {list(sub.columns)}")

    if sub["id"].duplicated().any():
        duplicated = sub.loc[sub["id"].duplicated(), "id"].tolist()
        raise ValueError(f"Duplicated IDs found: {duplicated[:10]}")

    if sub["votes"].isna().any():
        raise ValueError("Missing vote values found.")

    invalid_votes = sub.loc[~sub["votes"].astype(str).str.fullmatch(r"\d+")]
    if len(invalid_votes) > 0:
        raise ValueError(f"Votes must contain Arabic digits only. Invalid rows:\n{invalid_votes.head()}")

    if template_path is not None:
        template_path = Path(template_path)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")

        template = pd.read_csv(template_path, dtype={"id": str})
        expected_ids = set(template["id"].astype(str))
        actual_ids = set(sub["id"].astype(str))

        missing = sorted(expected_ids - actual_ids)
        extra = sorted(actual_ids - expected_ids)

        if missing:
            raise ValueError(f"Missing IDs: {missing[:20]}")
        if extra:
            raise ValueError(f"Extra IDs: {extra[:20]}")
        if len(sub) != len(template):
            raise ValueError(f"Expected {len(template)} rows, got {len(sub)} rows")

    print("Submission format is valid.")
    print(f"Rows: {len(sub):,}")
    print("Columns: id,votes")
    print("Votes: Arabic digits only")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("submission", help="Path to submission CSV")
    parser.add_argument("--template", default=None, help="Optional path to submission_template_v4.csv")
    args = parser.parse_args()

    validate_submission(args.submission, args.template)


if __name__ == "__main__":
    main()
