# Notebook Run Analysis - 2026-04-23

## Tong quan

- Da chay toan bo pipeline notebook theo thu tu `01 -> 07` bang kernel `datathon`.
- Co 2 loi chan pipeline va da duoc sua de notebook chay het:
  - `src/competition_workflow.py`: ham `run_baseline_models` tao `time_index` sau khi split, lam notebook 05 loi `KeyError` khi fit `LinearRegression`.
  - `notebooks/07_model_interpretation_and_final_submission.ipynb`: cell forecast de quy cho `COGS` dua `NaN` vao model `Ridge`; da bo sung fallback fill tu `modeling_dataset` va zero-fill cuoi.
- Sau khi fix, ca 7 notebook deu chay xong trong session hien tai.

## Notebook 01 - Data Understanding

- 13 bang du lieu duoc load thanh cong.
- Bang lon nhat: `order_items` 714,669 dong; `orders` 646,945 dong; `customers` 121,930 dong.
- Khoang thoi gian chinh:
  - `orders`: 2012-07-04 -> 2022-12-31
  - `sales`: 2012-07-04 -> 2022-12-31
  - `web_traffic`: 2013-01-01 -> 2022-12-31
- Diem can luu y ve chat luong du lieu:
  - `inventory.product_id` khong unique; day la bang snapshot theo thang nen khong the xem `product_id` la PK.
  - `order_items` co `23.04%` null cells, chu yeu o cac cot promotion.
  - `promotions` co `8%` null cells.
- Diem can luu y khi join:
  - `orders -> shipments`: match rate `87.50%`, thieu `80,878` don.
  - `orders -> reviews`: match rate `17.21%`, reviews khong phu toan bo don.
  - `orders -> returns`: match rate `5.57%`, returns la su kien hiem.
  - `sales -> web_traffic`: thieu `181` ngay traffic.
  - `customers -> geography` phai join bang `zip`; mapping theo `geography_id` trong plan goc khong ton tai.
- Artifact da sinh: `dataset_summary.csv`, `foreign_key_profile.csv`, `join_map.csv`, `table_usage.csv`.

## Notebook 02 - MCQ

- Notebook da tinh xong gia tri cho ca 10 cau.
- Ket qua tinh toan hien co:
  - Q1: typical inter-order gap = `144` ngay.
  - Q2: segment gross margin cao nhat = `Trendy (0.1547)`.
  - Q3: ly do return pho bien nhat cua Streetwear = `wrong_size`.
  - Q4: traffic source bounce rate thap nhat = `email_campaign (0.0045)`.
  - Q5: ti le dong order-item co promotion = `0.3866`.
  - Q6: nhom tuoi co so don trung binh cao nhat = `55+ (7.2687)`.
  - Q7: region doanh thu cao nhat = `East (7,291,150,819.12)`.
  - Q8: payment method pho bien nhat trong cancelled orders = `credit_card`.
  - Q9: size co return rate cao nhat = `S (0.0565)`.
  - Q10: installment plan co payment value trung binh cao nhat = `6 installments (24446.65)`.
- Van de con ton tai:
  - `artifacts/mcq/final_answers_mcq.csv` van de cot `Answer = TBD` cho ca 10 cau.
  - Nghia la notebook da tinh gia tri, nhung deliverable MCQ chua san sang nop neu can dap an A/B/C/D.

## Notebook 03 - EDA Planning

- Da tao day du 4 theme EDA:
  - Revenue & Demand
  - Customer & Channel
  - Returns & Customer Experience
  - Inventory & Operations
- Da tao `16` chart plan va bo `join_preparation.csv`.
- Taxonomy insight da duoc dat uu tien tu descriptive den prescriptive.
- Notebook nay dat muc tieu planning, khong gap loi thuc thi.

## Notebook 04 - Business EDA

- Da sinh ra day du cac bang trung gian trong `artifacts/eda/` va chart trong `charts/`.
- Tin hieu business noi bat tu cac bang artifact:
  - Channel:
    - `email_campaign` co bounce rate thap nhat: `0.004458`.
    - `direct` co bounce rate cao nhat trong bang da doc: `0.004511`.
  - Region:
    - `East` dan dau doanh thu: `7.29B`.
    - `Central`: `4.72B`.
    - `West`: `3.67B`.
  - Returns:
    - Streetwear co `7,626` return do `wrong_size` voi refund amount `140.35M`.
    - Nhom non-Streetwear cung co `wrong_size` cao nhat, nhung nho hon nhieu (`6,341`).
  - Operations:
    - `Streetwear` co `36,993` stockout days, cao nhat he thong.
    - `Streetwear` co estimated lost revenue ~ `121.20B`, vuot xa cac category khac.
  - Segment net revenue:
    - `Everyday` cao nhat: `4.98B` net revenue.
    - `Balanced` dung thu hai: `4.75B`.
- Nhan xet:
  - Streetwear la cum rui ro lon nhat, vua return cao vua stockout cao.
  - East dang la vung uu tien cho ca doanh thu va phan bo nguon luc.

## Notebook 05 - Forecasting Baseline

- Ban dau notebook loi tai baseline regression; da fix trong `src/competition_workflow.py`.
- Sau khi fix, baseline chay xong va ket qua holdout la:
  - `Naive`: MAE `669,592`, RMSE `1,020,221`, R2 `0.6264`.
  - `Moving Average (7)`: RMSE `1,306,300`, R2 `0.3875`.
  - `Linear Regression`: RMSE `1,703,663`, R2 `-0.0418`.
  - `Seasonal Naive`: RMSE `1,788,122`, R2 `-0.1477`.
- Baseline tot nhat hien tai la `Naive`.
- `charts/baseline_forecast.png` da duoc sinh.

## Notebook 06 - Feature Engineering va Modeling

- Notebook chay xong, tao ra:
  - `modeling_dataset.parquet`
  - `feature_list.csv`
  - `model_vs_baseline.csv`
  - `models/model_candidate.pkl`
- Ket qua CV 5 folds:
  - `XGBoost`: MAE `735,242`, RMSE `1,051,396`, R2 `0.7549`.
  - `LightGBM`: RMSE `1,052,064`, R2 `0.7544`.
  - `Ridge`: RMSE `1,100,910`, R2 `0.7249`.
- Co canh bao `LinAlgWarning` tu `Ridge` do ma tran ill-conditioned, nhung khong chan pipeline.
- Diem can luu y:
  - File `model_vs_baseline.csv` hien tai chi chua 3 model ung vien, khong chua dong baseline.
  - Ten artifact cho thay so sanh voi baseline, nhung noi dung thuc te chua co bang so sanh truc tiep cung mot protocol danh gia.

## Notebook 07 - Final Model, SHAP, Submission

- Ban dau notebook loi o forecast de quy cho `COGS` do feature row con `NaN`; da fix truc tiep trong notebook.
- Sau khi fix, notebook da sinh cac artifact cuoi:
  - `submission.csv`
  - `validation_final.csv`
  - `feature_importance_final.csv`
  - `shap_summary.png`
  - `shap_waterfall_sample.png`
  - `models/final_model.pkl`
- Validation cuoi hien ghi lai model tot nhat:
  - `XGBoost`: RMSE `1,051,396`, R2 `0.7549`.
- Top feature importance cua model cuoi:
  - `revenue_lag_1`: `0.57998`
  - `daily_line_revenue`: `0.09342`
  - `quarter`: `0.03260`
  - `dayofmonth`: `0.02807`
  - `cogs_lag_7`: `0.01862`
- Kiem tra format submission:
  - So dong `submission.csv` = `548`, khop `sample_submission.csv`.
  - Cot du lieu = `Date, Revenue, COGS`, khop sample.
- Canh bao chat luong du bao rat manh:
  - Toan bo `548/548` dong du bao deu co `Revenue < COGS`.
  - Average predicted margin = `-1,970,842.62`.
  - Nghia la file nop dung format, nhung ve business plausibility thi rat yeu; can xem lai cach forecast `COGS`, cach rang buoc giua `Revenue` va `COGS`, hoac cach dung model cuoi.

## Ket luan tong hop

- Ve mat thuc thi, pipeline notebook hien da chay duoc tu dau den cuoi sau 2 fix ky thuat.
- Ve mat deliverable, co 3 diem chua tot:
  - MCQ chua dien dap an A/B/C/D.
  - File `model_vs_baseline.csv` chua thuc su so sanh voi baseline nhu ten goi.
  - `submission.csv` dung format nhung du bao kinh doanh khong hop ly vi `Revenue` thap hon `COGS` o tat ca dong.
- Ve mat insight business, 3 tin hieu lon nhat hien tai la:
  - `East` la vung doanh thu cao nhat.
  - `Streetwear` la cum van de lon nhat ve return va stockout.
  - `email_campaign` la channel co bounce rate tot nhat trong artifact da tao.

## File da thay doi trong qua trinh xu ly

- `src/competition_workflow.py`
- `notebooks/07_model_interpretation_and_final_submission.ipynb`
- `notebook_run_analysis_2026-04-23.md`