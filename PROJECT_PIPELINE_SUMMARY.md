# Tổng quan pipeline hiện tại của project DATATHON 2026 - NEU-BRT

Tài liệu này tổng hợp cách project hiện tại đang được xử lý dựa trên toàn bộ notebook và artifact trong repo. Mục tiêu của project là xử lý bộ dữ liệu thương mại điện tử thời trang, trả lời MCQ, xây dựng EDA/business insight và tạo mô hình dự báo `Revenue`/`COGS` để sinh file `submission.csv`.

## 1. Cấu trúc xử lý tổng thể

Pipeline hiện tại đi theo luồng sau:

1. Đọc hiểu dữ liệu và kiểm tra chất lượng bảng.
2. Trả lời phần MCQ bằng truy vấn trực tiếp trên dữ liệu.
3. Lập kế hoạch EDA và báo cáo phân tích.
4. Xây dựng EDA kinh doanh bằng R/ggplot.
5. Tạo baseline forecast cho `Revenue`.
6. Tạo feature engineering model cho `Revenue`.
7. Train model cuối cho `Revenue` và `COGS`, sinh `submission.csv`.
8. Lưu artifact, biểu đồ, mô hình và file nộp.

Các file đầu ra quan trọng:

- `submission.csv`: file nộp Kaggle hiện tại.
- `artifacts/final_submission/submission.csv`: bản copy của file nộp.
- `artifacts/modeling/model_results_summary.md`: tóm tắt kết quả model.
- `artifacts/final_submission/recursive_backtest_2022_scores.csv`: recursive validation gần hơn với bài toán submit.
- `models/final_revenue_model.joblib`, `models/final_cogs_model.joblib`: model cuối đã lưu.

## 2. Notebook `01_data_understanding.ipynb`

Notebook này làm nhiệm vụ audit dữ liệu đầu vào.

Các bước chính:

- Load toàn bộ file CSV trong `dataset/`.
- Parse các cột ngày như `Date`, `order_date`, `return_date`, `review_date`, `snapshot_date`, `start_date`, `end_date`.
- Kiểm tra số dòng, số cột, tên cột của từng bảng.
- Kiểm tra primary key ứng viên.
- Kiểm tra foreign key và join map giữa các bảng.
- Kiểm tra missing values.
- Kiểm tra date range của từng bảng.
- Phân loại bảng dùng cho MCQ, EDA và forecasting.

Các bảng dữ liệu chính:

| Bảng | Số dòng | Vai trò |
|---|---:|---|
| `orders` | 646,945 | đơn hàng |
| `order_items` | 714,669 | chi tiết sản phẩm trong đơn |
| `payments` | 646,945 | thanh toán |
| `shipments` | 566,067 | vận chuyển |
| `customers` | 121,930 | khách hàng |
| `reviews` | 113,551 | đánh giá |
| `inventory` | 60,247 | tồn kho |
| `returns` | 39,939 | hoàn trả |
| `sales` | 3,833 | doanh thu/ngày, target forecasting |
| `web_traffic` | 3,652 | traffic website |
| `products` | 2,412 | master sản phẩm |
| `promotions` | 50 | chương trình khuyến mãi |
| `sample_submission` | 548 | schema và ngày cần nộp |

Artifact chính:

- `artifacts/data_understanding/dataset_summary.csv`
- `artifacts/data_understanding/date_ranges.csv`
- `artifacts/data_understanding/missing_values.csv`
- `artifacts/data_understanding/primary_key_profile.csv`
- `artifacts/data_understanding/foreign_key_profile.csv`
- `artifacts/data_understanding/join_map.csv`
- `artifacts/data_understanding/table_usage.csv`

## 3. Notebook `02_mcq_solution.ipynb`

Notebook này xử lý phần câu hỏi trắc nghiệm bằng phân tích trực tiếp trên dữ liệu.

Các nhóm câu hỏi đã xử lý:

- Khoảng cách giữa các lần mua hàng.
- Gross margin theo segment sản phẩm.
- Lý do hoàn trả phổ biến của streetwear.
- Bounce rate theo traffic source.
- Tỷ lệ dùng promo trong order items.
- Số đơn hàng theo nhóm tuổi.
- Doanh thu theo region.
- Payment method trong đơn bị cancel.
- Return rate theo size.
- Payment value theo installment plan.

Artifact chính:

- `artifacts/mcq/mcq_answers.csv`

## 4. Notebook `03_eda_planning.ipynb`

Notebook này là bước lập kế hoạch cho phần EDA và báo cáo.

Nội dung chính:

- Tóm tắt rubric phần EDA.
- Xác định bảng nào phục vụ phân tích nào.
- Chia EDA thành các theme lớn.
- Lên kế hoạch chart.
- Lên kế hoạch join.
- Xác định insight nào nên đưa vào báo cáo.
- Đảm bảo đủ các cấp độ phân tích: descriptive, diagnostic, predictive, prescriptive.

Các theme EDA chính:

1. Revenue and demand.
2. Customer and channel.
3. Returns and customer experience.
4. Inventory and operations.

Artifact chính:

- `artifacts/eda_planning/eda_plan.csv`
- `artifacts/eda_planning/chart_plan.csv`
- `artifacts/eda_planning/join_plan.csv`
- `artifacts/eda_planning/report_insights.csv`
- `artifacts/eda_planning/priority_plan.csv`

## 5. Notebook `04_business_eda.ipynb`

Notebook này thực hiện EDA bằng R và tạo biểu đồ phục vụ báo cáo.

Các insight chính:

| Insight | Chủ đề | Nội dung |
|---|---|---|
| I1 | Revenue and demand | Demand có tính mùa vụ, category mix tập trung |
| I2 | Customer and channel | Channel cần đánh giá theo revenue, AOV, repeat behavior, traffic quality |
| I3 | Returns and experience | Return pressure liên quan đến product fit và refund cost |
| I4 | Returns and experience | Delivery delay ảnh hưởng đến rating |
| I5 | Inventory and operations | Stockout tạo rủi ro revenue lớn ở top category |
| I6 | Inventory and operations | Overstock và sell-through thấp gây rủi ro vốn lưu động |

Biểu đồ được lưu trong:

- `artifacts/business_eda/charts/`

Artifact chính:

- `artifacts/business_eda/business_insight_summary.csv`
- `artifacts/business_eda/final_chart_list.csv`

## 6. Notebook `05_forecasting_baseline.ipynb`

Notebook này tạo baseline dự báo `Revenue`.

Các bước chính:

- Load `sales.csv`.
- Kiểm tra missing dates và cấu trúc chuỗi thời gian.
- Phân tích trend và seasonality.
- Tách validation 365 ngày cuối.
- So sánh các baseline:
  - naive
  - moving average 7
  - moving average 30
  - seasonal naive 7
  - seasonal naive 30
  - linear time features

Kết quả baseline tốt nhất:

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| `linear_time_features` | 1,016,413 | 1,416,690 | 0.284 |

Artifact chính:

- `artifacts/forecast_baseline/baseline_score_table.csv`
- `artifacts/forecast_baseline/baseline_validation_predictions_wide.csv`
- `artifacts/forecast_baseline/baseline_validation_predictions_long.csv`
- `artifacts/forecast_baseline/selected_baseline.csv`
- `artifacts/forecast_baseline/charts/`

## 7. Notebook `06_forecasting_feature_engineering.ipynb`

Notebook này là notebook modeling chính cho phần forecasting.

### 7.1 Dữ liệu sử dụng

Notebook load các bảng nội bộ:

- `sales.csv`
- `web_traffic.csv`
- `orders.csv`
- `order_items.csv`
- `products.csv`
- `payments.csv`
- `promotions.csv`
- `inventory.csv`
- `returns.csv`
- `reviews.csv`
- `shipments.csv`

### 7.2 Feature engineering

Feature được tạo theo daily grain, một dòng cho mỗi ngày.

Nhóm feature chính:

- Calendar features:
  - `day_of_week`
  - `day_of_month`
  - `day_of_year`
  - `week_of_year`
  - `month`
  - `quarter`
  - `year`
  - `is_weekend`
  - `time_index`

- Sales lag/rolling features:
  - `revenue_lag_1`, `revenue_lag_7`, `revenue_lag_14`, `revenue_lag_28`, `revenue_lag_30`, `revenue_lag_60`, `revenue_lag_90`, `revenue_lag_365`
  - `cogs_lag_1`, `cogs_lag_7`, `cogs_lag_14`, `cogs_lag_28`, `cogs_lag_30`, `cogs_lag_60`, `cogs_lag_90`, `cogs_lag_365`
  - rolling mean/std cho Revenue
  - rolling mean cho COGS
  - `revenue_ewm_7`, `revenue_ewm_30`

- Operational/exogenous features:
  - web traffic daily aggregates
  - order/order item/payment aggregates
  - active promotions
  - inventory monthly mapped to daily
  - returns/reviews/shipments aggregates

Để giảm leakage, các operational raw features không được dùng trực tiếp cùng ngày. Notebook tạo bản:

- `*_lag_1`
- `*_roll_mean_7`

### 7.3 Validation setup

Validation hiện tại:

- Train: từ sau khi đủ lag 365 đến `2021-12-31`.
- Validation: `2022-01-01` đến `2022-12-31`.

Notebook 06 chọn model theo one-step validation. Nghĩa là khi dự báo ngày trong validation, lag của target vẫn dựa trên actual trong validation. Điều này hữu ích để so sánh model nhanh, nhưng có thể optimistic so với submit thật.

### 7.4 Model được thử

Các model:

- Linear Regression
- Ridge
- Random Forest
- XGBoost

Kết quả feature engineering model:

| Rank | Model | MAE | RMSE | R2 |
|---:|---|---:|---:|---:|
| 1 | `xgboost` | 563,080 | 781,609 | 0.782 |
| 2 | `ridge` | 609,093 | 810,858 | 0.765 |
| 3 | `linear_regression` | 632,169 | 831,720 | 0.753 |
| 4 | `random_forest` | 593,006 | 846,197 | 0.744 |

Model tốt nhất theo notebook 06: `xgboost`.

So với baseline tốt nhất, RMSE giảm khoảng 44.83%.

Artifact chính:

- `artifacts/modeling/modeling_dataset_daily.csv`
- `artifacts/modeling/modeling_dataset_ready.csv`
- `artifacts/modeling/feature_list.csv`
- `artifacts/modeling/model_results_feature_engineering.csv`
- `artifacts/modeling/model_vs_baseline_comparison.csv`
- `artifacts/modeling/validation_predictions_feature_engineering.csv`
- `artifacts/modeling/best_candidate_for_notebook_07.csv`
- `models/best_feature_engineering_model.joblib`

## 8. Notebook `07_model_interpretation_and_final_submission.ipynb`

Notebook này tạo model cuối và sinh file submission.

### 8.1 Chọn model

Notebook đọc:

- `artifacts/modeling/best_candidate_for_notebook_07.csv`

Model được chọn hiện tại:

- `xgboost`

### 8.2 Feature trong final pipeline

Final pipeline load:

- `sales.csv`
- `sample_submission.csv`
- `promotions.csv`

Feature final gồm:

- calendar features
- sales lag/rolling features
- active promotion calendar features

Lưu ý: final pipeline không dùng toàn bộ operational/exogenous features từ notebook 06. Vì vậy feature set giữa notebook 06 và notebook 07 chưa hoàn toàn giống nhau.

### 8.3 Validation trong final notebook

Final notebook có one-step validation cho:

- `Revenue`
- `COGS`

Kết quả one-step:

| Target | Model | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| Revenue | `xgboost` | 551,478 | 756,691 | 0.796 |
| COGS | `xgboost` | 479,393 | 652,306 | 0.800 |

Ngoài ra, project có artifact recursive backtest 2022:

| Target | Model | Validation mode | MAE | RMSE | R2 |
|---|---|---|---:|---:|---:|
| Revenue | `xgboost` | recursive walk-forward | 630,098 | 863,343 | 0.734 |
| COGS | `xgboost` | recursive walk-forward | 556,873 | 740,160 | 0.742 |

Recursive backtest là con số thực tế hơn cho bài toán submit dài ngày, vì prediction ngày trước được đưa lại vào lịch sử để tạo feature cho ngày sau.

### 8.4 Sinh submission

Notebook refit model trên toàn bộ training data hợp lệ, sau đó dự báo theo thứ tự ngày trong `sample_submission.csv`.

Cách dự báo:

1. Bắt đầu với lịch sử `sales.csv`.
2. Lấy ngày đầu tiên trong test.
3. Tạo feature từ lịch sử hiện có.
4. Dự báo `Revenue` và `COGS`.
5. Append prediction vào lịch sử.
6. Lặp lại cho ngày tiếp theo.

File được ghi ra:

- `submission.csv`
- `artifacts/final_submission/submission.csv`

Validation file submission:

- đúng số dòng
- đúng thứ tự ngày
- đúng cột `Date`, `Revenue`, `COGS`
- không missing
- không có giá trị âm

### 8.5 Explainability

Notebook tạo:

- feature importance
- permutation importance
- partial dependence plots
- business interpretation

Artifact chính:

- `artifacts/final_submission/final_feature_list.csv`
- `artifacts/final_submission/final_feature_importance.csv`
- `artifacts/final_submission/final_permutation_importance.csv`
- `artifacts/final_submission/business_interpretation.csv`
- `artifacts/final_submission/final_pipeline_config.json`
- `artifacts/final_submission/charts/`
- `models/final_revenue_model.joblib`
- `models/final_cogs_model.joblib`

## 9. Notebook `preprocessing_summary.ipynb`

Notebook này là tài liệu tóm tắt preprocessing, không phải nơi xử lý dữ liệu chính.

Nội dung:

- Data understanding
- Cleaning
- Preprocessing
- Forecasting feature engineering
- Model preprocessing
- Leakage controls

Artifact liên quan:

- `artifacts/preprocessing/preprocessing_summary.csv`
- `artifacts/preprocessing/preprocessing_summary.md`

## 10. Notebook `baseline.ipynb`

Đây là một notebook baseline riêng ở root repo.

Logic chính:

- Load `sales.csv` và `sample_submission.csv`.
- Tạo seasonal profile theo tháng/ngày.
- Dự báo test dựa trên seasonal pattern.
- Evaluate trên tail training 2021-2022.
- Export `submission.csv`.

Notebook này có vẻ là baseline thử nghiệm độc lập, không phải pipeline final chính hiện tại. Pipeline final chính đang nằm ở `notebooks/05`, `notebooks/06`, `notebooks/07`.

## 11. File submission hiện tại

File submit hiện tại:

- `submission.csv`
- `artifacts/final_submission/submission.csv`

File này đã được khôi phục về bản cũ có public score `1,027,271.86127`.

Cấu trúc:

```csv
Date,Revenue,COGS
2023-01-01,2161341.0,2056678.88
2023-01-02,1809318.12,1805893.88
...
```

Ý nghĩa:

- `Date`: ngày cần dự báo.
- `Revenue`: doanh thu dự báo.
- `COGS`: giá vốn hàng bán dự báo.

Kaggle dùng file này để so sánh với test ẩn và tính score.

## 12. Điểm mạnh của project hiện tại

Các điểm tốt:

- Dữ liệu được audit tương đối đầy đủ.
- Có mapping rõ bảng nào dùng cho MCQ, EDA, Forecasting.
- Có EDA plan và business insight có cấu trúc.
- Có baseline rõ ràng để so sánh.
- Có feature engineering model cải thiện mạnh so với baseline.
- Có kiểm soát leakage cơ bản:
  - Không dùng `sample_submission` target làm feature.
  - Sales lag/rolling được shift.
  - Operational features trong notebook 06 được lag/rolling thay vì dùng same-day raw.
- Final submission được sinh recursive theo thứ tự ngày.
- Có artifact phục vụ báo cáo: feature importance, permutation importance, partial dependence, business interpretation.

## 13. Lỗ hổng và rủi ro hiện tại

### 13.1 Model selection vẫn dựa chủ yếu vào one-step validation

Notebook 06 chọn model theo one-step validation. Trong one-step validation, các lag trong validation dùng actual quá khứ thật. Trong submit thật, sau ngày đầu tiên, lag dùng prediction trước đó.

Hệ quả:

- Validation score có thể đẹp hơn thực tế.
- Model có thể được chọn vì giỏi one-step nhưng chưa chắc giỏi recursive dài hạn.

### 13.2 Phụ thuộc mạnh vào short lag

Feature importance hiện tại cho thấy `revenue_lag_1` là feature quan trọng nhất.

Các feature rủi ro cao:

- `revenue_lag_1`
- `cogs_lag_1`
- `revenue_lag_7`
- `cogs_lag_7`
- rolling 7 ngày
- rolling 14 ngày

Các feature này dễ gây error accumulation khi forecast 548 ngày.

### 13.3 Feature set giữa notebook 06 và 07 chưa đồng nhất

Notebook 06 dùng nhiều operational/exogenous features đã lag:

- web traffic
- orders
- payments
- returns
- reviews
- shipments
- inventory

Notebook 07 final chỉ dùng:

- sales lag/rolling
- calendar
- promotions

Vì vậy model được chọn trong notebook 06 không hoàn toàn cùng feature space với model final trong notebook 07.

### 13.4 Future exogenous features không chắc chắn

Các bảng operational kết thúc ở `2022-12-31`. Test bắt đầu từ `2023-01-01`.

Do đó, nếu dùng trực tiếp hoặc mô phỏng kém các feature như web traffic, order count, payments, inventory, returns, reviews, shipments thì có rủi ro cao.

Hiện final notebook tránh phần lớn rủi ro này bằng cách không dùng các feature đó, nhưng notebook 06 vẫn dùng để chọn model.

### 13.5 Promotions trong tương lai gần như không có

`promotions.csv` kết thúc ở `2022-12-31`. Trong test 2023-2024, active promotion features có thể gần như toàn 0.

Điều này có thể tạo distribution shift nếu model học promotion là tín hiệu mạnh.

### 13.6 Forecast level có dấu hiệu hơi cao

Submission hiện tại có Revenue trung bình cao hơn:

- khoảng 20.8% so với năm 2022
- khoảng 28.4% so với giai đoạn 2019-2022

Một số tháng như October, November, December cao hơn 2022 khá nhiều. Đây là rủi ro nếu test thật không tăng trưởng mạnh.

## 14. Kết luận hiện trạng

Project hiện tại đã có pipeline đầy đủ từ data understanding, MCQ, EDA, baseline, feature engineering model đến final submission. Về mặt báo cáo và reproducibility, project có cấu trúc tương đối tốt.

Tuy nhiên, phần forecasting vẫn có rủi ro kỹ thuật:

- model selection còn optimistic do dựa nhiều vào one-step validation;
- model phụ thuộc mạnh vào short lag;
- feature set giữa notebook 06 và notebook 07 chưa đồng nhất;
- recursive forecast dài hạn có thể kém ổn định hơn validation một bước;
- submission hiện tại đang dùng bản score cũ tốt hơn các thử nghiệm mới.

Vì vậy, nếu mục tiêu là giữ score Kaggle hiện tại, nên tiếp tục dùng `submission.csv` hiện tại. Nếu mục tiêu là cải thiện pipeline về mặt kỹ thuật, bước tiếp theo nên là:

1. Đồng nhất feature set giữa notebook 06 và notebook 07.
2. Chọn model theo recursive validation thay vì one-step validation.
3. Giảm phụ thuộc vào `lag_1`, `lag_7` và rolling ngắn.
4. Chỉ giữ exogenous features có thể biết hoặc mô phỏng đáng tin trong tương lai.
5. So sánh submission candidate mới với bản cũ trước khi submit.
