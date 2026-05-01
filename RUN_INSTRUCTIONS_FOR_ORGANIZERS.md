# Hướng dẫn chạy lại file submission

Tài liệu này dành cho ban tổ chức/người chấm khi clone repo và muốn tái lập file `submission.csv`.

## 1. Yêu cầu môi trường

Khuyến nghị dùng Python 3.10 trở lên.

Cài thư viện:

```powershell
python -m pip install -r requirements.txt
```

## 2. Tạo lại file submission

Chạy lệnh sau tại thư mục gốc của repo:

```powershell
python scripts\make_final_submission.py
```

Lệnh này sẽ tạo/ghi đè 2 file:

```text
submission.csv
artifacts/final_submission/submission.csv
```

File `submission.csv` ở root repo là file dùng để nộp Kaggle.

## 3. Kiểm tra file submission

Sau khi tạo file, chạy:

```powershell
python scripts\validate_submissions.py
```

Script kiểm tra:

- đúng 548 dòng;
- đúng cột `Date`, `Revenue`, `COGS`;
- thứ tự ngày khớp `dataset/sample_submission.csv`;
- không có missing value;
- không có dự báo âm.

Report kiểm tra được lưu tại:

```text
artifacts/final_submission/submission_validation_report.csv
```

## 4. Nguồn dữ liệu dùng để tạo submission

Script `scripts/make_final_submission.py` đọc:

```text
artifacts/final_submission/sources/old_forecast_for_70_30.csv
artifacts/final_submission/sources/stable_recursive_recovered_from_download.csv
```

Quy tắc tạo final submission:

```text
Revenue = 70% old_forecast + 30% stable_recursive_forecast
COGS    = 100% old_forecast
```

## 5. Kết quả kỳ vọng

Sau khi chạy `make_final_submission.py`, file `submission.csv` hợp lệ sẽ có:

```text
Số dòng: 548
Cột: Date, Revenue, COGS
Revenue mean: 3,799,175.74
COGS mean: 3,193,734.72
```

Hash SHA256 của file `submission.csv` hiện tại:

```text
512F826C48EE7CA1E8038C354B485F9A4CECFEBB4FF32AE0214E020A6C6B1DB8
```

## 6. Ghi chú

- Repo không dùng dữ liệu ngoài.
- `dataset/sample_submission.csv` chỉ dùng để kiểm tra schema và thứ tự ngày.
- File nộp chính thức luôn là `submission.csv` ở thư mục gốc repo.
