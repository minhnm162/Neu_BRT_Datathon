#!/usr/bin/env python
"""python scripts/train.py"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils import load_config, set_seed, get_logger
from src.data_loader import load_all
from src.features.pipeline import build_feature_matrix
from src.models.gbm import train_lgbm_l1, train_lgbm_l2, train_lgbm_huber, get_feature_cols, save_model

import pandas as pd
import numpy as np

log = get_logger("train")


def main():
    cfg = load_config("config.yaml")
    set_seed(cfg["seed"])

    log.info("Loading data...")
    tables = load_all(cfg)

    log.info("Building features...")
    feat_path = "outputs/feature_matrix.parquet"
    df = build_feature_matrix(cfg, tables, save_path=feat_path)

    # Train/val split: train<=2021-12-31, val=2022
    train = df[df["Date"] <= "2021-12-31"].copy()
    val   = df[(df["Date"] >= "2022-01-01") & (df["Date"] <= "2022-12-31")].copy()

    feat_cols = get_feature_cols(df)
    X_tr, y_tr = train[feat_cols], train["Revenue"]
    X_vl, y_vl = val[feat_cols],   val["Revenue"]

    # Fill NaN
    X_tr = X_tr.fillna(0)
    X_vl = X_vl.fillna(0)

    log.info(f"Train: {len(train)} rows | Val: {len(val)} rows | Features: {len(feat_cols)}")

    log.info("Training LGBM L1...")
    m_l1 = train_lgbm_l1(X_tr, y_tr, X_vl, y_vl, seed=cfg["seed"])
    save_model(m_l1, "lgbm_l1", cfg["paths"]["models"])

    log.info("Training LGBM L2...")
    m_l2 = train_lgbm_l2(X_tr, y_tr, X_vl, y_vl, seed=cfg["seed"])
    save_model(m_l2, "lgbm_l2", cfg["paths"]["models"])

    log.info("Training LGBM Huber...")
    m_hub = train_lgbm_huber(X_tr, y_tr, X_vl, y_vl, seed=cfg["seed"])
    save_model(m_hub, "lgbm_huber", cfg["paths"]["models"])

    log.info("Training done. Models saved to outputs/models/")


if __name__ == "__main__":
    main()
