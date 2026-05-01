from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FINAL_DIR = ROOT / "artifacts" / "final_submission"
SOURCES_DIR = FINAL_DIR / "sources"

OLD_FORECAST_PATH = SOURCES_DIR / "old_forecast_for_70_30.csv"
STABLE_FORECAST_PATH = SOURCES_DIR / "stable_recursive_recovered_from_download.csv"
OUTPUT_PATH = FINAL_DIR / "submission.csv"
ROOT_OUTPUT_PATH = ROOT / "submission.csv"

REVENUE_OLD_WEIGHT = 0.70
REVENUE_STABLE_WEIGHT = 0.30


def validate_frame(name: str, frame: pd.DataFrame) -> None:
    expected_columns = ["Date", "Revenue", "COGS"]
    if list(frame.columns) != expected_columns:
        raise ValueError(f"{name} columns must be {expected_columns}, got {list(frame.columns)}")
    if len(frame) != 548:
        raise ValueError(f"{name} must have 548 rows, got {len(frame)}")
    if frame[expected_columns].isna().any().any():
        raise ValueError(f"{name} contains missing values")


def main() -> None:
    old = pd.read_csv(OLD_FORECAST_PATH)
    stable = pd.read_csv(STABLE_FORECAST_PATH)

    validate_frame("old forecast", old)
    validate_frame("stable forecast", stable)

    if not old["Date"].equals(stable["Date"]):
        raise ValueError("Forecast source files must have the same Date order")

    submission = old.copy()
    submission["Revenue"] = (
        REVENUE_OLD_WEIGHT * old["Revenue"]
        + REVENUE_STABLE_WEIGHT * stable["Revenue"]
    ).round(2)
    submission["COGS"] = old["COGS"].round(2)

    validate_frame("final submission", submission)

    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    submission.to_csv(OUTPUT_PATH, index=False)
    try:
        submission.to_csv(ROOT_OUTPUT_PATH, index=False)
        root_status = "updated"
    except PermissionError:
        root_status = "locked; updated artifacts/final_submission/submission.csv only"

    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Root submission.csv: {root_status}")
    print(f"Rows: {len(submission)}")
    print(f"Revenue mean: {submission['Revenue'].mean():.2f}")
    print(f"COGS mean: {submission['COGS'].mean():.2f}")


if __name__ == "__main__":
    main()
