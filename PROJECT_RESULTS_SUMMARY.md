# Tổng hợp kết quả bài làm

## 1. File nộp cuối

File nộp chính thức:

```text
submission.csv
```

File artifact tương ứng:

```text
artifacts/final_submission/submission.csv
```

Hai file này được tạo bằng:

```powershell
python scripts\make_final_submission.py
```

Quy tắc:

```text
Revenue = 70% old_forecast + 30% stable_recursive_forecast
COGS    = 100% old_forecast
```

Public Kaggle tốt nhất đã ghi nhận cho bản này:

```text
1,027,271.86127
```

## 2. MCQ

File chính:

- `notebooks/02_mcq_solution.ipynb`
- `artifacts/mcq/mcq_answers.csv`

Trạng thái:

- Đã có đủ Q1-Q10.
- Q7 được xử lý bằng join `order_items -> orders -> geography` vì `sales.csv` không có region.

## 3. EDA

File chính:

- `notebooks/03_eda_planning.ipynb`
- `notebooks/04_business_eda.ipynb`
- `notebooks/08_eda_supplementary.ipynb`
- `artifacts/business_eda/`
- `report/figures/`

Các nhóm insight:

1. Revenue and demand.
2. Customer and channel.
3. Returns and experience.
4. Delivery delay and rating.
5. Inventory stockout.
6. Overstock and sell-through.

Điểm mạnh:

- Có mạch phân tích từ doanh thu -> khách hàng/kênh -> trải nghiệm -> tồn kho -> hành động.
- Có insight dạng descriptive, diagnostic và prescriptive.
- Có chart và bảng summary để đưa vào báo cáo.

## 4. Forecasting

Baseline tốt nhất:

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| Linear time features | 1,016,413 | 1,416,690 | 0.284 |

Feature-engineering model tốt nhất:

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| XGBoost | 563,080 | 781,609 | 0.782 |

Validation cuối:

| Mode | Target | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| One-step | Revenue | 551,478 | 756,691 | 0.796 |
| Recursive | Revenue | 630,098 | 863,343 | 0.734 |
| One-step | COGS | 479,393 | 652,306 | 0.800 |
| Recursive | COGS | 556,873 | 740,160 | 0.742 |

Nhận xét:

- One-step validation đẹp hơn nhưng lạc quan hơn bài toán submit 548 ngày.
- Recursive validation phản ánh đúng rủi ro tích lũy lỗi hơn.
- Final submission chọn blend 70/30 vì public Kaggle thực tế tốt hơn các bản thử nghiệm sau đó.

## 5. File cần chấm nhanh

1. `submission.csv`
2. `README.md`
3. `PROJECT_PIPELINE_SUMMARY.md`
4. `PROJECT_RESULTS_SUMMARY.md`
5. `notebooks/02_mcq_solution.ipynb`
6. `notebooks/04_business_eda.ipynb`
7. `notebooks/07_model_interpretation_and_final_submission.ipynb`
8. `artifacts/final_submission/submission_validation_report.csv`
