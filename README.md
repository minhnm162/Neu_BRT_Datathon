# DATATHON 2026 Round 1 - NEU-BRT

Official solution repository of team **NEU-BRT** for **DATATHON 2026 Round 1**.

## Team

- Team name: **NEU-BRT**
- Competition: **DATATHON 2026 - Round 1**
- Submission deadline: **23:59, 01/05/2026**

## Objective

The project forecasts future e-commerce `Revenue` and `COGS` from historical business data covering orders, order items, products, customers, geography, payments, returns, reviews, inventory, shipments, promotions, web traffic, and sales.

The work is organized around three competition needs:

- MCQ answers
- EDA and business storytelling
- Forecasting and submission generation

## Key Outputs

| Area | Main Files |
|---|---|
| MCQ | `artifacts/mcq/mcq_answers.csv`, `notebooks/02_mcq_solution.ipynb` |
| Data understanding | `artifacts/data_understanding/` |
| Preprocessing summary | `artifacts/preprocessing/preprocessing_summary.md`, `artifacts/preprocessing/preprocessing_summary.csv` |
| Power BI / EDA tables | `aggregated_tables/`, `aggregated_tables/README.md` |
| Business EDA | `artifacts/business_eda/`, `artifacts/business_eda/charts/` |
| Baseline models | `artifacts/forecast_baseline/` |
| Feature engineering models | `artifacts/modeling/` |
| Model result summary | `artifacts/modeling/model_results_summary.md` |
| Final submission | `submission.csv`, `artifacts/final_submission/submission.csv` |

## Model Summary

Best baseline:

| Model | Target | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| linear_time_features | Revenue | 1,016,413 | 1,416,690 | 0.284 |

Best feature-engineering model:

| Model | Target | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| xgboost | Revenue | 563,080 | 781,609 | 0.782 |

Final recursive backtest:

| Target | Model | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| Revenue | xgboost | 630,098 | 863,343 | 0.734 |
| COGS | xgboost | 556,873 | 740,160 | 0.742 |

Compared with the best baseline, the best feature-engineering model reduces Revenue RMSE by about **44.83%**.

For a fuller summary, see `artifacts/modeling/model_results_summary.md`.

## Data Processing Notes

The raw competition files in `dataset/` are kept unchanged.

Processed tables for Power BI and EDA are stored in `aggregated_tables/`. Their grain and usage are documented in:

- `aggregated_tables/README.md`
- `aggregated_tables/table_grain_map.csv`

Preprocessing decisions are summarized in:

- `notebooks/preprocessing_summary.ipynb`
- `artifacts/preprocessing/preprocessing_summary.md`
- `artifacts/preprocessing/preprocessing_summary.csv`

## Leakage Controls

- `sample_submission` is used only for required dates and output schema.
- `sample_submission` `Revenue` and `COGS` values are ignored.
- Sales-derived lag and rolling features use past values only.
- Final future predictions are generated recursively.
- Recursive 2022 walk-forward backtest is exported to `artifacts/final_submission/recursive_backtest_2022_scores.csv`.

## Repository Structure

```text
dataset/                         Raw competition data
notebooks/                       Main analysis notebooks
scripts/                         Reproducibility and artifact scripts
aggregated_tables/               Processed Power BI / EDA tables
artifacts/data_understanding/     Data audit outputs
artifacts/preprocessing/          Preprocessing documentation
artifacts/business_eda/           Business insight outputs and charts
artifacts/forecast_baseline/      Baseline forecast outputs
artifacts/modeling/               Feature engineering model outputs
artifacts/final_submission/       Final validation and submission outputs
models/                           Saved model files
submission.csv                    Final root-level submission file
```

## Reproducibility

To regenerate processed artifacts without modifying raw data:

```powershell
python scripts\pipeline_review_fixes.py
```

Large generated tables, especially `aggregated_tables/order_lines_enriched.csv`, should be kept local or tracked with Git LFS. See `docs_git_large_file_fix.md`.
