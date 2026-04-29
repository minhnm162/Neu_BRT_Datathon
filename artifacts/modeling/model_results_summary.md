# Model Results Summary

This file summarizes the current forecasting results for quick review and reporting.

## Best Baseline

| Model | Target | MAE | RMSE | R2 |
|---|---|---:|---:|---:|
| linear_time_features | Revenue | 1,016,413 | 1,416,690 | 0.284 |

The best baseline is `linear_time_features` from notebook 05.

## Feature Engineering Model Comparison

| Rank | Model | MAE | RMSE | R2 |
|---:|---|---:|---:|---:|
| 1 | xgboost | 563,080 | 781,609 | 0.782 |
| 2 | ridge | 609,093 | 810,858 | 0.765 |
| 3 | linear_regression | 632,169 | 831,720 | 0.753 |
| 4 | random_forest | 593,006 | 846,197 | 0.744 |

The best feature-engineering model is `xgboost`.

Compared with the best baseline:

- MAE improves by about 44.60%.
- RMSE improves by about 44.83%.
- R2 improves from 0.284 to 0.782.

## Final Validation

| Target | Model | Validation Mode | MAE | RMSE | R2 |
|---|---|---|---:|---:|---:|
| Revenue | xgboost | teacher_forcing_one_step | 551,478 | 756,691 | 0.796 |
| COGS | xgboost | teacher_forcing_one_step | 479,393 | 652,306 | 0.800 |

This validation uses observed lag values inside the validation period. It is useful for model comparison but can be optimistic for multi-step forecasting.

## Recursive Backtest

| Target | Model | Validation Mode | MAE | RMSE | R2 |
|---|---|---|---:|---:|---:|
| Revenue | xgboost | recursive_walk_forward | 630,098 | 863,343 | 0.734 |
| COGS | xgboost | recursive_walk_forward | 556,873 | 740,160 | 0.742 |

The recursive walk-forward result is the more realistic number for future submission behavior because each prediction is fed back into the history before forecasting the next date.

## Top Drivers

From `artifacts/modeling/feature_importance.csv`, the strongest signals include:

- `payment_value_total_lag_1`
- `revenue_lag_1`
- `cogs_lag_365`
- `revenue_lag_365`
- `inv_units_received_lag_1`
- `revenue_lag_7`
- `revenue_lag_14`

The model is mainly driven by recent demand momentum, annual seasonality, payment-value history, and selected operational signals.

## Reviewer Note

For reporting, prefer citing the recursive backtest as the realistic validation estimate, while using the one-step score to compare model families.
