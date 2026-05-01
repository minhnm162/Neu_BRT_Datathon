"""Cac chi so danh gia: MAE, RMSE, R2, composite score."""
import numpy as np
import pandas as pd


def mae(y_true, y_pred) -> float:
    return float(np.mean(np.abs(np.array(y_true) - np.array(y_pred))))


def rmse(y_true, y_pred) -> float:
    return float(np.sqrt(np.mean((np.array(y_true) - np.array(y_pred)) ** 2)))


def r2(y_true, y_pred) -> float:
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot > 0 else 0.0


def composite_score(y_true, y_pred,
                    w_mae: float = 0.4,
                    w_rmse: float = 0.4,
                    w_r2: float = 0.2) -> float:
    """
    Score tong hop de toi uu ca 3 metrics dong thoi.
    Thap hon = tot hon (minimize).
    MAE/RMSE chuan hoa theo std cua y_true.
    """
    std = np.std(y_true) or 1.0
    mae_norm  = mae(y_true, y_pred) / std
    rmse_norm = rmse(y_true, y_pred) / std
    r2_neg    = max(0.0, 1 - r2(y_true, y_pred))
    return w_mae * mae_norm + w_rmse * rmse_norm + w_r2 * r2_neg


def evaluate(y_true, y_pred, label: str = "") -> dict:
    result = {
        "mae":       mae(y_true, y_pred),
        "rmse":      rmse(y_true, y_pred),
        "r2":        r2(y_true, y_pred),
        "composite": composite_score(y_true, y_pred),
    }
    if label:
        print(f"[{label}]  MAE={result['mae']:,.0f}  RMSE={result['rmse']:,.0f}"
              f"  R2={result['r2']:.4f}  Composite={result['composite']:.4f}")
    return result


def compare_models(results: dict) -> pd.DataFrame:
    """results = {model_name: {mae, rmse, r2, composite}}"""
    df = pd.DataFrame(results).T
    df = df.sort_values("composite")
    df["mae"]  = df["mae"].map("{:,.0f}".format)
    df["rmse"] = df["rmse"].map("{:,.0f}".format)
    df["r2"]   = df["r2"].map("{:.4f}".format)
    df["composite"] = df["composite"].map("{:.4f}".format)
    return df
