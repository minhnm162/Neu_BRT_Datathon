# DATATHON 2026 - NEU-BRT

Repo này chứa bài làm vòng 1 DATATHON 2026 của đội NEU-BRT, gồm 3 phần:

| Phần | Nội dung | File chính |
|---|---|---|
| 1 | MCQ | `notebooks/02_mcq_solution.ipynb`, `artifacts/mcq/mcq_answers.csv` |
| 2 | EDA và phân tích kinh doanh | `notebooks/04_business_eda.ipynb`, `notebooks/08_eda_supplementary.ipynb`, `artifacts/business_eda/` |
| 3 | Forecasting Revenue/COGS | `notebooks/05_forecasting_baseline.ipynb` -> `07_model_interpretation_and_final_submission.ipynb` |

## Cấu trúc repo

```text
Neu_BRT_Datathon/
├── dataset/                 # Dữ liệu gốc do BTC cung cấp
├── notebooks/               # Notebook theo thứ tự xử lý 01-08
├── artifacts/               # Kết quả trung gian và kết quả cuối
├── aggregated_tables/       # Bảng tổng hợp phục vụ EDA/Power BI/report
├── models/                  # Model đã train
├── report/figures/          # Hình xuất cho báo cáo
├── scripts/                 # Script tái lập và kiểm tra submission
├── submission.csv           # File nộp Kaggle chính thức
├── PROJECT_PIPELINE_SUMMARY.md
├── PROJECT_RESULTS_SUMMARY.md
└── requirements.txt
```

## Cài đặt

```powershell
python -m pip install -r requirements.txt
```

## Tái lập file submission

File nộp chính thức là:

```text
submission.csv
```

Tạo lại file này bằng:

```powershell
python scripts\make_final_submission.py
```

Script đọc 2 nguồn dự báo:

- `artifacts/final_submission/sources/old_forecast_for_70_30.csv`
- `artifacts/final_submission/sources/stable_recursive_recovered_from_download.csv`

Quy tắc blend cuối:

```text
Revenue = 70% old_forecast + 30% stable_recursive_forecast
COGS    = 100% old_forecast
```

Kết quả cũng được lưu tại:

```text
artifacts/final_submission/submission.csv
```

## Kiểm tra submission

```powershell
python scripts\validate_submissions.py
```

Script kiểm tra:

- đúng 548 dòng;
- đúng cột `Date, Revenue, COGS`;
- thứ tự ngày khớp `dataset/sample_submission.csv`;
- không missing;
- không có dự báo âm.

Report kiểm tra:

```text
artifacts/final_submission/submission_validation_report.csv
```

## Kết quả forecasting chính

| Mốc đánh giá | Target | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| One-step validation | Revenue | 551,478 | 756,691 | 0.796 |
| Recursive validation | Revenue | 630,098 | 863,343 | 0.734 |
| One-step validation | COGS | 479,393 | 652,306 | 0.800 |
| Recursive validation | COGS | 556,873 | 740,160 | 0.742 |

Public Kaggle tốt nhất đã ghi nhận cho bản final 70/30:

```text
1,027,271.86127
```

## Ghi chú rule

- Không dùng dữ liệu ngoài.
- `sample_submission.csv` chỉ dùng để lấy schema và thứ tự ngày.
- Source forecast và script tạo submission đều nằm trong repo để có thể tái lập.
