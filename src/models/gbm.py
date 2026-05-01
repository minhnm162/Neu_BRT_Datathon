"""
LightGBM / XGBoost / CatBoost wrappers voi nhieu loss functions.
Muc tieu: toi uu dong thoi MAE, RMSE, R2.
"""
import numpy as np
import pandas as pd
import pickle
from pathlib import Path
from typing import Optional, List

from src.metrics import evaluate
from src.utils import get_logger

log = get_logger("gbm")

IGNORE_COLS = ["Date", "Revenue", "COGS"]


def get_feature_cols(df: pd.DataFrame,
                     ignore: List[str] = None) -> List[str]:
    ignore = ignore or IGNORE_COLS
    return [c for c in df.columns if c not in ignore
            and df[c].dtype != object]


# ─── LightGBM ─────────────────────────────────────────────────────────────────

def train_lgbm(X_train: pd.DataFrame, y_train: pd.Series,
               X_val: pd.DataFrame, y_val: pd.Series,
               objective: str = "regression",
               params: dict = None,
               seed: int = 42) -> object:
    import lightgbm as lgb

    default_params = dict(
        objective=objective,
        n_estimators=3000,
        learning_rate=0.03,
        max_depth=6,
        num_leaves=63,
        min_child_samples=20,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=seed,
        verbose=-1,
        n_jobs=-1,
    )
    if params:
        default_params.update(params)

    model = lgb.LGBMRegressor(**default_params)
    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(100, verbose=False),
                   lgb.log_evaluation(period=-1)],
    )
    preds = model.predict(X_val)
    evaluate(y_val.values, preds, label=f"LGBM-{objective}")
    return model


def train_lgbm_l1(X_tr, y_tr, X_vl, y_vl, seed=42, params=None):
    """LightGBM L1 loss (toi uu MAE)."""
    return train_lgbm(X_tr, y_tr, X_vl, y_vl, "regression_l1", params, seed)


def train_lgbm_l2(X_tr, y_tr, X_vl, y_vl, seed=42, params=None):
    """LightGBM L2 loss (toi uu RMSE/R2)."""
    return train_lgbm(X_tr, y_tr, X_vl, y_vl, "regression", params, seed)


def train_lgbm_huber(X_tr, y_tr, X_vl, y_vl, alpha=1.0, seed=42, params=None):
    """LightGBM Huber loss (can bang MAE va RMSE)."""
    huber_params = {"alpha": alpha}
    if params:
        huber_params.update(params)
    return train_lgbm(X_tr, y_tr, X_vl, y_vl, "huber", huber_params, seed)


# ─── XGBoost ──────────────────────────────────────────────────────────────────

def train_xgb(X_train: pd.DataFrame, y_train: pd.Series,
              X_val: pd.DataFrame, y_val: pd.Series,
              seed: int = 42, params: dict = None) -> object:
    import xgboost as xgb

    default_params = dict(
        objective="reg:squarederror",
        n_estimators=3000,
        learning_rate=0.03,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=seed,
        n_jobs=-1,
        early_stopping_rounds=100,
        eval_metric="rmse",
        verbosity=0,
    )
    if params:
        default_params.update(params)

    model = xgb.XGBRegressor(**default_params)
    model.fit(X_train, y_train,
              eval_set=[(X_val, y_val)],
              verbose=False)
    preds = model.predict(X_val)
    evaluate(y_val.values, preds, label="XGBoost")
    return model


# ─── CatBoost ─────────────────────────────────────────────────────────────────

def train_catboost(X_train: pd.DataFrame, y_train: pd.Series,
                   X_val: pd.DataFrame, y_val: pd.Series,
                   seed: int = 42, params: dict = None) -> object:
    from catboost import CatBoostRegressor

    default_params = dict(
        loss_function="RMSE",
        iterations=3000,
        learning_rate=0.03,
        depth=6,
        l2_leaf_reg=3,
        subsample=0.8,
        random_seed=seed,
        early_stopping_rounds=100,
        verbose=False,
    )
    if params:
        default_params.update(params)

    model = CatBoostRegressor(**default_params)
    model.fit(X_train, y_train,
              eval_set=(X_val, y_val))
    preds = model.predict(X_val)
    evaluate(y_val.values, preds, label="CatBoost")
    return model


# ─── Save / Load ──────────────────────────────────────────────────────────────

def save_model(model, name: str, models_dir: str = "outputs/models"):
    Path(models_dir).mkdir(parents=True, exist_ok=True)
    path = f"{models_dir}/{name}.pkl"
    with open(path, "wb") as f:
        pickle.dump(model, f)
    log.info(f"Saved {name} to {path}")


def load_model(name: str, models_dir: str = "outputs/models") -> object:
    path = f"{models_dir}/{name}.pkl"
    with open(path, "rb") as f:
        return pickle.load(f)
