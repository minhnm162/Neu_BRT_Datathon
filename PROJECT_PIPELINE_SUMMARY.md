# Tổng quan pipeline

## 1. Luồng xử lý

Project đi theo thứ tự:

1. Đọc hiểu dữ liệu và kiểm tra schema.
2. Trả lời MCQ bằng truy vấn trực tiếp trên dữ liệu gốc.
3. Xây dựng EDA và insight kinh doanh.
4. Tạo baseline forecasting.
5. Tạo feature engineering cho Revenue/COGS.
6. Train model XGBoost và đánh giá one-step/recursive validation.
7. Tạo final submission bằng blend 70/30.

## 2. Notebook

| Notebook | Vai trò |
|---|---|
| `01_data_understanding.ipynb` | Kiểm tra bảng, khóa, missing, date range |
| `02_mcq_solution.ipynb` | Tính đáp án MCQ Q1-Q10 |
| `03_eda_planning.ipynb` | Lập kế hoạch EDA |
| `04_business_eda.ipynb` | EDA chính và insight kinh doanh |
| `05_forecasting_baseline.ipynb` | Baseline forecast |
| `06_forecasting_feature_engineering.ipynb` | Feature engineering và model comparison |
| `07_model_interpretation_and_final_submission.ipynb` | Model cuối, interpretation, submission |
| `08_eda_supplementary.ipynb` | Bổ sung chart/action matrix cho phần EDA |

## 3. Forecasting pipeline

Target:

- `Revenue`
- `COGS`

Feature chính:

- Calendar: month, quarter, day of week, seasonality.
- Lag/rolling của target.
- Business features từ order, payment, promotion, traffic, inventory.

Validation:

- One-step validation dùng actual lịch sử để tạo feature cho từng ngày validation.
- Recursive validation mô phỏng gần hơn submit dài hạn vì prediction ngày trước được dùng để tạo lag cho ngày sau.

Rủi ro đã nhận diện:

- One-step validation có thể quá lạc quan.
- Lag ngắn hạn giúp validation tốt nhưng có thể tích lũy lỗi khi forecast xa.
- Future exogenous features không chắc chắn, nên final submission ưu tiên blend ổn định.

## 4. Final submission

File chính:

```text
submission.csv
```

Tái lập:

```powershell
python scripts\make_final_submission.py
```

Blend:

```text
Revenue = 70% old_forecast + 30% stable_recursive_forecast
COGS    = 100% old_forecast
```

Lý do chọn:

- Validation one-step tốt nhưng không sát bài toán submit dài hạn.
- Recursive ổn định hơn nhưng public score riêng không tốt bằng.
- Blend 70/30 là bản public Kaggle tốt nhất đã ghi nhận trong quá trình thử nghiệm.

## 5. Artifact quan trọng

| File | Nội dung |
|---|---|
| `artifacts/mcq/mcq_answers.csv` | Đáp án MCQ |
| `artifacts/business_eda/business_insight_summary.csv` | Summary insight EDA |
| `artifacts/final_submission/final_validation_scores.csv` | One-step validation |
| `artifacts/final_submission/recursive_backtest_2022_scores.csv` | Recursive validation |
| `artifacts/final_submission/final_feature_importance.csv` | Feature importance |
| `artifacts/final_submission/submission.csv` | Bản copy submission |
| `artifacts/final_submission/sources/` | Source forecast để tái lập blend |
