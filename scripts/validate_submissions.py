from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PATH = ROOT / "dataset" / "sample_submission.csv"
SUBMISSION_PATHS = [
    ROOT / "submission.csv",
    ROOT / "artifacts" / "final_submission" / "submission.csv",
]
REQUIRED_COLUMNS = ["Date", "Revenue", "COGS"]


def validate(path: Path, sample: pd.DataFrame) -> dict:
    if not path.exists():
        return {"file": str(path.relative_to(ROOT)), "exists": False}

    df = pd.read_csv(path)
    date_order_matches = False
    if "Date" in df.columns and len(df) == len(sample):
        date_order_matches = df["Date"].astype(str).tolist() == sample["Date"].astype(str).tolist()

    return {
        "file": str(path.relative_to(ROOT)),
        "exists": True,
        "rows": len(df),
        "columns_match": list(df.columns) == REQUIRED_COLUMNS,
        "row_count_matches": len(df) == len(sample),
        "date_order_matches": date_order_matches,
        "no_missing_values": bool(df.isna().sum().sum() == 0),
        "non_negative_predictions": bool((df[["Revenue", "COGS"]] >= 0).all().all())
        if all(col in df.columns for col in ["Revenue", "COGS"])
        else False,
        "revenue_mean": float(df["Revenue"].mean()) if "Revenue" in df.columns else None,
        "cogs_mean": float(df["COGS"].mean()) if "COGS" in df.columns else None,
    }


def main() -> None:
    sample = pd.read_csv(SAMPLE_PATH)
    results = pd.DataFrame(validate(path, sample) for path in SUBMISSION_PATHS)
    output_path = ROOT / "artifacts" / "final_submission" / "submission_validation_report.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    print(results.to_string(index=False))
    print(f"\nWrote validation report: {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
