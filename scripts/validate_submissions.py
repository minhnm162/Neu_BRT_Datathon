# Script kiểm tra định dạng và tính hợp lệ của các file nộp bài.
# So sánh submission.csv với sample_submission.csv về số hàng, thứ tự ngày,
# giá trị thiếu và tính không âm của dự báo.
from __future__ import annotations

from pathlib import Path

import pandas as pd


# --- Đường dẫn ---
ROOT = Path(__file__).resolve().parents[1]
# File mẫu từ ban tổ chức (dùng để đối chiếu số hàng và thứ tự Date)
SAMPLE_PATH = ROOT / "dataset" / "sample_submission.csv"
# Danh sách các file nộp cần kiểm tra
SUBMISSION_PATHS = [
    ROOT / "submission.csv",
    ROOT / "artifacts" / "final_submission" / "submission.csv",
]
# Các cột bắt buộc trong file nộp
REQUIRED_COLUMNS = ["Date", "Revenue", "COGS"]


def validate(path: Path, sample: pd.DataFrame) -> dict:
    """Kiểm tra một file nộp và trả về dict kết quả.

    Các tiêu chí kiểm tra:
    - File tồn tại.
    - Số hàng khớp với sample_submission.csv (548 hàng).
    - Tên và thứ tự cột đúng: Date, Revenue, COGS.
    - Thứ tự ngày khớp với sample_submission.csv.
    - Không có giá trị thiếu.
    - Revenue và COGS không âm.
    """
    if not path.exists():
        return {"file": str(path.relative_to(ROOT)), "exists": False}

    df = pd.read_csv(path)
    # Kiểm tra thứ tự Date có khớp với sample hay không
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
        # Kiểm tra Revenue và COGS đều không âm (nếu cả 2 cột tồn tại)
        "non_negative_predictions": bool((df[["Revenue", "COGS"]] >= 0).all().all())
        if all(col in df.columns for col in ["Revenue", "COGS"])
        else False,
        "revenue_mean": float(df["Revenue"].mean()) if "Revenue" in df.columns else None,
        "cogs_mean": float(df["COGS"].mean()) if "COGS" in df.columns else None,
    }


def main() -> None:
    # Đọc file mẫu để lấy chuẩn đối chiếu
    sample = pd.read_csv(SAMPLE_PATH)
    # Chạy kiểm tra trên tất cả các file nộp và tạo báo cáo
    results = pd.DataFrame(validate(path, sample) for path in SUBMISSION_PATHS)
    output_path = ROOT / "artifacts" / "final_submission" / "submission_validation_report.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    # In kết quả ra màn hình và lưu báo cáo
    print(results.to_string(index=False))
    print(f"\nWrote validation report: {output_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
