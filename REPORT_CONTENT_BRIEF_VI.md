# Nội dung cần thiết để viết báo cáo DATATHON 2026

Tài liệu này gom các thông tin quan trọng nhất từ notebook, artifact và file submission hiện tại để phục vụ viết báo cáo. Mục tiêu là giúp phần báo cáo đi theo mạch: hiểu dữ liệu -> phân tích kinh doanh -> xây dựng mô hình -> đánh giá -> đề xuất hành động.

## 1. Bối cảnh bài toán

Doanh nghiệp là một công ty thương mại điện tử thời trang tại Việt Nam. Bài toán forecasting yêu cầu dự báo `Revenue` và `COGS` theo ngày cho giai đoạn từ **01/01/2023 đến 01/07/2024**, tổng cộng **548 ngày**.

Dữ liệu train nằm trong giai đoạn **04/07/2012 đến 31/12/2022**. Bảng mục tiêu chính là `sales.csv`, gồm doanh thu và giá vốn theo ngày.

Mục tiêu kinh doanh của dự báo:

- Lập kế hoạch doanh thu theo ngày.
- Chuẩn bị tồn kho trước mùa cao điểm.
- Hỗ trợ quyết định khuyến mãi.
- Giảm rủi ro thiếu hàng, tồn kho chậm bán và chi phí vận hành.

## 2. Tổng quan dữ liệu

Repo sử dụng toàn bộ dữ liệu do ban tổ chức cung cấp, không dùng dữ liệu ngoài. Tổng cộng có **14 bảng** với khoảng **2,960,736 dòng**.

Một số bảng chính:

| Bảng | Số dòng | Vai trò |
|---|---:|---|
| `orders` | 646,945 | Thông tin đơn hàng |
| `order_items` | 714,669 | Chi tiết sản phẩm trong đơn |
| `payments` | 646,945 | Thanh toán |
| `shipments` | 566,067 | Vận chuyển |
| `customers` | 121,930 | Khách hàng |
| `reviews` | 113,551 | Đánh giá |
| `inventory` | 60,247 | Tồn kho theo tháng/sản phẩm |
| `returns` | 39,939 | Hoàn trả |
| `sales` | 3,833 | Doanh thu và COGS theo ngày |
| `web_traffic` | 3,652 | Traffic website |
| `sample_submission` | 548 | Schema và ngày cần dự báo |

Khoảng thời gian chính:

| Bảng | Từ ngày | Đến ngày | Số ngày |
|---|---|---|---:|
| `sales.csv` | 2012-07-04 | 2022-12-31 | 3,833 |
| `sample_submission.csv` | 2023-01-01 | 2024-07-01 | 548 |

Thống kê `sales.csv`:

| Chỉ số | Revenue | COGS |
|---|---:|---:|
| Mean | 4,286,584 | 3,695,134 |
| Median | 3,647,304 | 3,161,113 |
| Std | 2,624,840 | 2,219,789 |
| Min | 279,814 | 236,576 |
| Max | 20,905,271 | 16,535,858 |

Nhận xét có thể đưa vào báo cáo:

- Doanh thu có biến động lớn giữa các ngày, thể hiện qua độ lệch chuẩn cao.
- Phân phối Revenue có đuôi phải dài, nghĩa là tồn tại các ngày doanh thu rất cao so với mặt bằng trung vị.
- Vì bài toán là forecast dài hạn 548 ngày, validation cần mô phỏng đúng việc dự báo nhiều bước thay vì chỉ dự báo một ngày tiếp theo.

## 3. MCQ

Notebook chính:

- `notebooks/02_mcq_solution.ipynb`

Artifact:

- `artifacts/mcq/mcq_answers.csv`

Kết quả Q1-Q10:

| Câu | Đáp án | Bằng chứng chính |
|---|---|---|
| Q1 | C | Median gap giữa các lần mua là 144 ngày, gần option 180 ngày nhất |
| Q2 | D | Segment `standard` có gross margin trung bình cao nhất, khoảng 0.3134 |
| Q3 | B | Lý do hoàn trả nhiều nhất của streetwear là `wrong_size`, 7,626 records |
| Q4 | C | `email_campaign` có bounce rate trung bình khoảng 0.004458 |
| Q5 | C | Promo usage rate khoảng 38.66%, gần 39% |
| Q6 | A | Nhóm tuổi `55+` có average orders per customer khoảng 5.4069 |
| Q7 | C | Region `east` đứng đầu theo proxy doanh thu transaction-level |
| Q8 | A | `credit_card` có số cancelled orders cao nhất, 28,452 |
| Q9 | A | Size `s` có return rate khoảng 0.0565 |
| Q10 | C | 6 installments có average payment value khoảng 24,446.65 |

Lưu ý cho Q7:

- `sales.csv` không có cột region.
- Cách xử lý là tính proxy doanh thu theo dòng giao dịch bằng `sum(quantity * unit_price)`, sau đó join `order_items -> orders -> geography`.
- Đây là cách diễn giải hợp lý vì region nằm ở bảng `geography`, còn transaction value nằm ở `order_items`.
- Trong báo cáo nên ghi rõ Q7 dùng doanh thu transaction-level proxy để tránh hiểu nhầm.

## 4. EDA và insight kinh doanh

Notebook chính:

- `notebooks/03_eda_planning.ipynb`
- `notebooks/04_business_eda.ipynb`
- `notebooks/08_eda_supplementary.ipynb`

Artifact chính:

- `artifacts/business_eda/business_insight_summary.csv`
- `artifacts/business_eda/final_chart_list.csv`
- `report/figures/`

### 4.1. Mạch phân tích đề xuất cho báo cáo

Nên trình bày phần EDA theo mạch:

1. Doanh thu biến động theo mùa vụ và nhóm sản phẩm.
2. Kênh bán hàng và hành vi khách hàng tạo ra chất lượng doanh thu khác nhau.
3. Returns và rating phản ánh vấn đề trải nghiệm khách hàng.
4. Tồn kho và stockout ảnh hưởng trực tiếp đến khả năng bảo vệ doanh thu.
5. Từ insight chuyển thành action: chuẩn bị hàng, tối ưu kênh, giảm return, cải thiện vận hành.

### 4.2. Sáu insight chính

| ID | Chủ đề | Metric chính | Recommendation |
|---|---|---|---|
| I1 | Revenue and demand | Peak month revenue, category revenue share | Ưu tiên category đóng góp doanh thu cao trước các tháng peak |
| I2 | Customer and channel | Revenue, AOV, orders/customer, bounce rate | Phân bổ ngân sách theo chất lượng doanh thu, AOV, repeat behavior và traffic quality |
| I3 | Returns and experience | Return rate, return records, refund amount | Cải thiện hướng dẫn size cho nhóm size-category có return cao |
| I4 | Returns and experience | Rating theo delivery delay bucket | Chủ động thông báo hoặc ưu tiên vận chuyển cho đơn có rủi ro delay |
| I5 | Inventory and operations | Stockout days, fill rate, lost sales proxy | Tăng safety stock và reorder sớm cho category demand cao nhưng stockout nhiều |
| I6 | Inventory and operations | Overstock months, sell-through rate | Markdown hoặc giảm nhập nhóm overstock, đồng thời replenish nhóm bán tốt |

### 4.3. Chart nên đưa vào báo cáo

| Chart | Nội dung | Vai trò trong story |
|---|---|---|
| `insight_01_monthly_revenue.png` | Seasonality và peak revenue | Nền tảng cho demand planning |
| `insight_02_channel_value.png` | Channel value và repeat behavior | Ra quyết định marketing/channel |
| `insight_03_return_rate.png` | Return pressure theo product group | Giảm refund và friction |
| `insight_04_delay_rating.png` | Delivery delay và rating | Tín hiệu trải nghiệm logistics |
| `insight_05_lost_sales_stockout.png` | Stockout-based lost sales proxy | Bảo vệ doanh thu qua vận hành tồn kho |
| `insight_06_overstock_sellthrough.png` | Overstock và sell-through imbalance | Tối ưu working capital |

Hình bổ sung trong `report/figures/`:

- `D7_seasonality_heatmap.png`
- `G5_bcg_matrix.png`
- `P2_rfm_segmentation.png`
- `P4_cohort_retention.png`
- `PR5_action_priority_matrix.png`

### 4.4. Câu chữ có thể dùng trong báo cáo EDA

Revenue không chỉ phụ thuộc vào xu hướng thời gian mà còn bị chi phối bởi mùa vụ, category mix, chất lượng traffic, return behavior và khả năng đáp ứng tồn kho. Vì vậy, các recommendation không nên chỉ tập trung vào tăng bán hàng mà cần kết hợp giữa demand planning, channel optimization, return reduction và inventory control.

Các insight EDA cũng giải thích vì sao mô hình forecasting sử dụng nhóm feature calendar, lag/rolling, promotion, order/payment, traffic và inventory-derived features. Điều này giúp phần EDA và phần modeling liên kết với nhau thay vì tồn tại riêng lẻ.

## 5. Forecasting pipeline

Notebook chính:

- `notebooks/05_forecasting_baseline.ipynb`
- `notebooks/06_forecasting_feature_engineering.ipynb`
- `notebooks/07_model_interpretation_and_final_submission.ipynb`

Model chính:

- XGBoost cho `Revenue`
- XGBoost cho `COGS`

Nhóm feature chính:

- Calendar features: month, quarter, day of week, day of month, seasonality.
- Lag features: `revenue_lag_1`, `revenue_lag_7`, `revenue_lag_14`, `revenue_lag_28`, `revenue_lag_365`, các lag tương tự cho COGS.
- Rolling features: rolling mean/std theo các cửa sổ thời gian.
- Business features: promotion calendar, traffic/order/payment/inventory-derived features khi có thể tạo từ dữ liệu cung cấp.

## 6. Kết quả model

### 6.1. Baseline

Baseline tốt nhất trong notebook 05:

| Model | MAE | RMSE | R2 |
|---|---:|---:|---:|
| Linear time features | 1,016,413 | 1,416,690 | 0.284 |

Các baseline naive, seasonal naive và moving average có RMSE cao hơn. Điều này cho thấy dữ liệu có seasonal/time structure nhưng cần mô hình học feature tốt hơn để bắt được biến động doanh thu.

### 6.2. Feature engineering model

Model comparison trong notebook 06:

| Rank | Model | MAE | RMSE | R2 |
|---:|---|---:|---:|---:|
| 1 | XGBoost | 563,080 | 781,609 | 0.782 |
| 2 | Ridge | 609,093 | 810,858 | 0.765 |
| 3 | Linear Regression | 632,169 | 831,720 | 0.753 |
| 4 | Random Forest | 593,006 | 846,197 | 0.744 |
| 5 | Baseline linear time features | 1,016,413 | 1,416,690 | 0.284 |

So với baseline tốt nhất, XGBoost giảm RMSE khoảng **44.83%** và giảm MAE khoảng **44.60%** trên validation one-step.

### 6.3. Final validation

| Mode | Target | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| One-step | Revenue | 551,478 | 756,691 | 0.796 |
| One-step | COGS | 479,393 | 652,306 | 0.800 |
| Recursive walk-forward | Revenue | 630,098 | 863,343 | 0.734 |
| Recursive walk-forward | COGS | 556,873 | 740,160 | 0.742 |

Nhận xét kỹ thuật:

- One-step validation tốt hơn vì mỗi ngày validation vẫn có thể sử dụng actual lịch sử gần đó để tạo lag feature.
- Recursive validation thực tế hơn cho bài toán submit 548 ngày vì prediction của ngày trước được dùng làm input cho ngày sau.
- Khoảng cách giữa one-step và recursive cho thấy mô hình có rủi ro error accumulation khi forecast dài hạn.
- Vì vậy, khi chọn final submission không chỉ nhìn one-step metric mà cần cân nhắc recursive validation và public Kaggle feedback.

## 7. Feature importance và giải thích mô hình

Top feature quan trọng nhất cho Revenue:

| Feature | Importance |
|---|---:|
| `revenue_lag_1` | 0.4791 |
| `cogs_lag_365` | 0.1206 |
| `revenue_lag_365` | 0.0340 |
| `revenue_lag_7` | 0.0258 |
| `revenue_lag_14` | 0.0247 |
| `cogs_lag_7` | 0.0224 |
| `revenue_lag_28` | 0.0172 |
| `day_of_month` | 0.0163 |
| `cogs_lag_28` | 0.0133 |
| `active_promo_types` | 0.0116 |

Top feature quan trọng nhất cho COGS:

| Feature | Importance |
|---|---:|
| `cogs_lag_1` | 0.3755 |
| `cogs_lag_365` | 0.1851 |
| `revenue_lag_1` | 0.0966 |
| `cogs_lag_7` | 0.0279 |
| `cogs_lag_28` | 0.0162 |
| `day_of_month` | 0.0160 |
| `revenue_lag_365` | 0.0155 |
| `cogs_lag_14` | 0.0144 |

Diễn giải business:

- Recent revenue momentum là tín hiệu mạnh nhất: doanh thu gần nhất giúp mô hình neo kỳ vọng ngắn hạn.
- Lag 365 ngày cho thấy yếu tố mùa vụ theo năm có vai trò quan trọng.
- Calendar features giúp mô hình điều chỉnh theo weekday/month/season.
- Promotion features giúp mô hình phản ứng với campaign intensity khi thông tin này nằm trong dữ liệu được cung cấp.
- COGS lag giúp giữ quan hệ Revenue/COGS nhất quán hơn.

Điểm cần thừa nhận trong report:

- Mô hình phụ thuộc khá mạnh vào lag ngắn hạn như `revenue_lag_1`.
- Với horizon 548 ngày, phụ thuộc vào lag ngắn hạn có thể làm lỗi tích lũy.
- Do đó, final strategy dùng blend giữa forecast cũ và stable recursive forecast để giảm rủi ro lệch quá mạnh.

## 8. Final submission

File nộp:

```text
submission.csv
```

Artifact copy:

```text
artifacts/final_submission/submission.csv
```

Cách tái lập:

```powershell
python scripts\make_final_submission.py
```

Quy tắc final:

```text
Revenue = 70% old_forecast + 30% stable_recursive_forecast
COGS    = 100% old_forecast
```

Lý do chọn blend:

- XGBoost one-step có validation đẹp nhưng có thể optimistic.
- Stable recursive forecast mô phỏng horizon dài tốt hơn nhưng public score riêng không tốt bằng.
- Blend 70/30 giữ phần lớn signal từ forecast cũ, đồng thời thêm một phần forecast ổn định hơn.
- Public Kaggle tốt nhất đã ghi nhận cho bản này là **1,027,271.86127**.

Thống kê final submission:

| Chỉ số | Revenue | COGS |
|---|---:|---:|
| Mean | 3,799,176 | 3,193,735 |
| Median | 3,620,418 | 3,013,402 |
| Std | 1,540,810 | 1,322,882 |
| Min | 1,202,495 | 850,968 |
| Max | 9,791,556 | 8,742,578 |

Kết quả validate file submission:

- 548 dòng.
- Đúng cột `Date`, `Revenue`, `COGS`.
- Thứ tự ngày khớp `dataset/sample_submission.csv`.
- Không có missing value.
- Không có prediction âm.
- `submission.csv` và `artifacts/final_submission/submission.csv` giống nhau.

## 9. Reproducibility

Lệnh cài dependencies:

```powershell
python -m pip install -r requirements.txt
```

Lệnh tạo final submission:

```powershell
python scripts\make_final_submission.py
```

Lệnh kiểm tra submission:

```powershell
python scripts\validate_submissions.py
```

Source để tái lập blend:

- `artifacts/final_submission/sources/old_forecast_for_70_30.csv`
- `artifacts/final_submission/sources/stable_recursive_recovered_from_download.csv`

Report validate:

- `artifacts/final_submission/submission_validation_report.csv`

## 10. Kết luận nên viết trong báo cáo

Bài làm xây dựng pipeline từ data understanding, MCQ, EDA đến forecasting. Phần EDA chỉ ra các yếu tố kinh doanh ảnh hưởng đến doanh thu như mùa vụ, category mix, kênh bán hàng, return behavior, delivery delay và tình trạng tồn kho. Các insight này được chuyển thành feature hoặc định hướng cho mô hình forecasting.

Về modeling, XGBoost là mô hình tốt nhất trên validation one-step, giảm mạnh MAE/RMSE so với baseline. Tuy nhiên, do bài toán submit yêu cầu forecast 548 ngày, recursive validation được dùng để kiểm tra rủi ro tích lũy lỗi. Final submission chọn chiến lược blend 70/30 giữa forecast cũ và stable recursive forecast nhằm cân bằng giữa độ chính xác public leaderboard và tính ổn định dài hạn.

Kết quả cuối cùng là file `submission.csv` hợp lệ, có thể tái lập bằng script, không dùng dữ liệu ngoài và tuân thủ schema của ban tổ chức.
