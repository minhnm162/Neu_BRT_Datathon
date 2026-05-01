"""TimeSeriesSplit expanding window va cross-validation utilities."""
import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from src.metrics import evaluate


def expanding_cv_splits(df: pd.DataFrame,
                        date_col: str,
                        folds: List[dict]) -> List[Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Tra ve list (train_df, val_df) theo expanding window.
    folds: [{"train_end": ..., "val_start": ..., "val_end": ...}, ...]
    """
    splits = []
    for fold in folds:
        train_end  = pd.Timestamp(fold["train_end"])
        val_start  = pd.Timestamp(fold["val_start"])
        val_end    = pd.Timestamp(fold["val_end"])
        train = df[df[date_col] <= train_end].copy()
        val   = df[(df[date_col] >= val_start) & (df[date_col] <= val_end)].copy()
        splits.append((train, val))
    return splits


def cross_validate(model_fn, X: pd.DataFrame, y: pd.Series,
                   date_col: str, folds: List[dict],
                   label: str = "model") -> Dict[str, float]:
    """
    Cross validate mot model tren cac folds expanding window.
    model_fn(X_train, y_train) -> fitted model
    model.predict(X_val) -> array-like
    """
    fold_results = []
    for i, fold in enumerate(folds):
        train_end  = pd.Timestamp(fold["train_end"])
        val_start  = pd.Timestamp(fold["val_start"])
        val_end    = pd.Timestamp(fold["val_end"])

        mask_train = X[date_col] <= train_end
        mask_val   = (X[date_col] >= val_start) & (X[date_col] <= val_end)

        X_tr, y_tr = X[mask_train].drop(columns=[date_col]), y[mask_train]
        X_vl, y_vl = X[mask_val].drop(columns=[date_col]),  y[mask_val]

        if len(X_tr) == 0 or len(X_vl) == 0:
            continue

        model = model_fn(X_tr, y_tr)
        preds = model.predict(X_vl)
        res   = evaluate(y_vl.values, preds, label=f"{label} fold{i+1}")
        fold_results.append(res)

    # Trung binh qua cac folds
    avg = {k: float(np.mean([r[k] for r in fold_results])) for k in fold_results[0]}
    print(f"\n[{label}] CV Mean -> MAE={avg['mae']:,.0f}  RMSE={avg['rmse']:,.0f}"
          f"  R2={avg['r2']:.4f}  Composite={avg['composite']:.4f}\n")
    return avg
