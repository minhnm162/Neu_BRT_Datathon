# Script tạo file nộp cuối cùng bằng cách blend 2 forecast sources.
# Blend weights: Revenue = 70% old + 30% stable; COGS = 100% old.
from pathlib import Path

import pandas as pd


# --- Đường dẫn ---
ROOT = Path(__file__).resolve().parents[1]
FINAL_DIR = ROOT / "artifacts" / "final_submission"
SOURCES_DIR = FINAL_DIR / "sources"

# Nguồn forecast 1: file dự báo cũ (weight cao hơn cho Revenue)
OLD_FORECAST_PATH = SOURCES_DIR / "old_forecast_for_70_30.csv"
# Nguồn forecast 2: file dự báo stable recursive (đã recover từ Kaggle download)
STABLE_FORECAST_PATH = SOURCES_DIR / "stable_recursive_recovered_from_download.csv"
# Đường dẫn file nộp đầu ra
OUTPUT_PATH = FINAL_DIR / "submission.csv"
ROOT_OUTPUT_PATH = ROOT / "submission.csv"

# Tỷ trọng blend cho cột Revenue
REVENUE_OLD_WEIGHT = 0.70
REVENUE_STABLE_WEIGHT = 0.30


def validate_frame(name: str, frame: pd.DataFrame) -> None:
    """Kiểm tra định dạng DataFrame trước khi blend hoặc lưu.

    Yêu cầu: đúng 3 cột (Date, Revenue, COGS), đúng 548 hàng,
    không có giá trị thiếu.
    """
    expected_columns = ["Date", "Revenue", "COGS"]
    if list(frame.columns) != expected_columns:
        raise ValueError(f"{name} columns must be {expected_columns}, got {list(frame.columns)}")
    if len(frame) != 548:
        raise ValueError(f"{name} must have 548 rows, got {len(frame)}")
    if frame[expected_columns].isna().any().any():
        raise ValueError(f"{name} contains missing values")


def main() -> None:
    # Đọc 2 nguồn forecast
    old = pd.read_csv(OLD_FORECAST_PATH)
    stable = pd.read_csv(STABLE_FORECAST_PATH)

    # Kiểm tra định dạng từng nguồn
    validate_frame("old forecast", old)
    validate_frame("stable forecast", stable)

    # Đảm bảo thứ tự ngày khớp nhau
    if not old["Date"].equals(stable["Date"]):
        raise ValueError("Forecast source files must have the same Date order")

    # Tạo file nộp: blend Revenue, giữ nguyên COGS từ nguồn old
    submission = old.copy()
    submission["Revenue"] = (
        REVENUE_OLD_WEIGHT * old["Revenue"]
        + REVENUE_STABLE_WEIGHT * stable["Revenue"]
    ).round(2)
    submission["COGS"] = old["COGS"].round(2)

    # Kiểm tra định dạng file nộp cuối cùng
    validate_frame("final submission", submission)

    # Ghi file nộp ra đĩa
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    submission.to_csv(OUTPUT_PATH, index=False)
    try:
        submission.to_csv(ROOT_OUTPUT_PATH, index=False)
        root_status = "updated"
    except PermissionError:
        root_status = "locked; updated artifacts/final_submission/submission.csv only"

    # In tóm tắt kết quả
    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    print(f"Root submission.csv: {root_status}")
    print(f"Rows: {len(submission)}")
    print(f"Revenue mean: {submission['Revenue'].mean():.2f}")
    print(f"COGS mean: {submission['COGS'].mean():.2f}")


if __name__ == "__main__":
    main()
