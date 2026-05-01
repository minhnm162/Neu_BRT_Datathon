#!/usr/bin/env python
"""python scripts/predict.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from pathlib import Path

from src.utils import load_config, set_seed, get_logger, save_submission
from src.data_loader import load_sales, load_sample_submission
from src.models.gbm import load_model, get_feature_cols
from src.features.pipeline import build_feature_matrix
from src.data_loader import load_all
from src.models.ensemble import blend_predictions

log = get_logger("predict")


def main():
    cfg = load_config("config.yaml")
    set_seed(cfg["seed"])

    log.info("Loading feature matrix...")
    feat_path = "outputs/feature_matrix.parquet"
    if Path(feat_path).exists():
        df = pd.read_parquet(feat_path)
    else:
        tables = load_all(cfg)
        df = build_feature_matrix(cfg, tables, save_path=feat_path)

    # Load models
    models = {}
    for name in ["lgbm_l1", "lgbm_l2", "lgbm_huber"]:
        try:
            models[name] = load_model(name, cfg["paths"]["models"])
            log.info(f"Loaded {name}")
        except Exception as e:
            log.warning(f"Could not load {name}: {e}")

    if not models:
        log.error("No models found. Run scripts/train.py first.")
        return

    # Test set
    test = df[df["Date"] >= cfg["test_start"]].copy()
    feat_cols = get_feature_cols(df)
    X_test = test[feat_cols].fillna(0)

    log.info(f"Test set: {len(test)} rows | Features: {len(feat_cols)}")

    # Ensemble predictions (balanced weights)
    preds_list = [m.predict(X_test) for m in models.values()]
    weights = np.ones(len(preds_list)) / len(preds_list)
    final_preds = blend_predictions(preds_list, weights)

    # COGS = Revenue * rolling ratio
    train_data = df[df["Date"] <= cfg["train_end"]]
    cogs_ratio = (train_data["COGS"] / (train_data["Revenue"] + 1e-6)).rolling(90, min_periods=30).mean().iloc[-1]
    final_cogs = final_preds * cogs_ratio

    log.info(f"COGS ratio (rolling 90d): {cogs_ratio:.4f}")

    # Build submission
    submission = load_sample_submission(cfg)[["Date"]].copy()
    test_preds = pd.DataFrame({
        "Date":    test["Date"].values,
        "Revenue": final_preds,
        "COGS":    final_cogs
    })
    submission = submission.merge(test_preds, on="Date", how="left")

    # Clip negatives
    submission["Revenue"] = submission["Revenue"].clip(lower=0)
    submission["COGS"]    = submission["COGS"].clip(lower=0)

    log.info(f"Submission shape: {submission.shape}")
    log.info(f"Revenue range: {submission['Revenue'].min():,.0f} - {submission['Revenue'].max():,.0f}")
    log.info(f"NaN check — Revenue: {submission['Revenue'].isna().sum()}, COGS: {submission['COGS'].isna().sum()}")

    save_submission(submission, "submission_final", cfg)


if __name__ == "__main__":
    main()
