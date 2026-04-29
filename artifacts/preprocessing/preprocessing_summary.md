# Preprocessing Summary

This document records the current data-processing pipeline without modifying any raw files in `dataset/`.

## What Counts As Data Understanding

- Load all raw CSV tables and parse known date columns.
- Check table shape, columns, sample rows, primary-key candidates, foreign-key match rates, missing values, and date ranges.
- Main outputs:
  - `artifacts/data_understanding/load_summary.csv`
  - `artifacts/data_understanding/dataset_summary.csv`
  - `artifacts/data_understanding/primary_key_profile.csv`
  - `artifacts/data_understanding/foreign_key_profile.csv`
  - `artifacts/data_understanding/date_ranges.csv`

## What Counts As Cleaning

- The raw competition files are not edited.
- Missing values are profiled with business meaning before any fill/drop decision.
- Important null handling:
  - `order_items.promo_id`: null means no primary promotion.
  - `order_items.promo_id_2`: null means no stacked or second promotion.
  - `promotions.applicable_category`: likely broad or all-category promotion metadata.
- These nulls should not be blanket-filled.

## What Counts As Preprocessing

- Build a join map and table usage map for MCQ, EDA, and forecasting.
- Convert raw relational tables into analysis-ready tables with explicit grain.
- Main outputs:
  - `aggregated_tables/order_lines_enriched.csv`: one row per order item line.
  - `aggregated_tables/returns_enriched.csv`: one row per return record.
  - `aggregated_tables/inventory_monthly_enriched.csv`: one row per month, category, segment.
  - `aggregated_tables/table_grain_map.csv`: documented grain and primary use.

## What Counts As Forecasting Feature Engineering

- Forecasting target grain is one row per date.
- Sales-derived features are shifted so the model uses past values only.
- Feature groups:
  - Calendar features: weekday, month, quarter, year, weekend flag, time index.
  - Lag features: Revenue and COGS lags.
  - Rolling features: rolling mean and rolling standard deviation.
  - EWM features: exponentially weighted Revenue features.
  - Promotion calendar features: active campaign counts and promotion metadata counts.
- Main outputs:
  - `aggregated_tables/daily_sales_features_final_grain.csv`
  - `artifacts/final_submission/final_feature_list.csv`

## What Counts As Model Preprocessing

- Numeric imputation is done inside sklearn pipelines using `SimpleImputer(strategy="median")`.
- Scaling is used only for linear/ridge candidates in notebook 06.
- Tree-based and XGBoost models use imputation but do not require scaling.

## Leakage Controls

- `sample_submission` is used only for required dates and output schema.
- `sample_submission` Revenue and COGS values are ignored.
- Future submission predictions are generated recursively.
- A recursive 2022 walk-forward backtest is now exported:
  - `artifacts/final_submission/recursive_backtest_2022_scores.csv`
  - `artifacts/final_submission/recursive_backtest_2022_predictions.csv`

## Competition Reviewer Takeaway

The project has preprocessing, but it is intentionally goal-specific rather than generic:

- MCQ uses targeted joins and aggregations.
- EDA uses enriched analytical tables and business-level grains.
- Forecasting uses daily target grain, past-only sales features, controlled promotion calendar features, pipeline imputation, and recursive validation.
