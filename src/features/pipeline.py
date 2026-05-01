"""
Pipeline tong hop: build full feature matrix cho modeling.
"""
import numpy as np
import pandas as pd
from pathlib import Path

from src.data_loader import load_all
from src.features.calendar import add_calendar_features
from src.features.lags import add_all_lag_features
from src.features.transactional import (
    build_daily_orders,
    build_daily_web_traffic,
    build_daily_inventory,
    build_daily_promotions,
    add_lagged_transactional,
)
from src.utils import load_config, get_logger

log = get_logger("feature_pipeline")


def build_feature_matrix(cfg: dict = None, tables: dict = None,
                         save_path: str = None) -> pd.DataFrame:
    """
    Build full feature matrix cho ca train + test range.
    Tranh leakage: cac transactional features duoc lag 1 ngay.
    """
    if cfg is None:
        cfg = load_config()
    if tables is None:
        tables = load_all(cfg)

    sales      = tables["sales"]
    submission = tables["submission"]
    orders     = tables["orders"]
    order_items = tables["order_items"]
    payments   = tables["payments"]
    customers  = tables["customers"]
    geography  = tables["geography"]
    promotions = tables["promotions"]
    web_traffic = tables["web_traffic"]
    inventory  = tables["inventory"]

    # ─── 1. Base DataFrame: gop train + test dates ───
    train_df = sales[["Date", "Revenue", "COGS"]].copy()
    test_df  = submission[["Date"]].copy()
    test_df["Revenue"] = np.nan
    test_df["COGS"]    = np.nan

    base = pd.concat([train_df, test_df], ignore_index=True)
    base = base.sort_values("Date").reset_index(drop=True)
    log.info(f"Base df: {len(base)} rows ({base['Date'].min().date()} to {base['Date'].max().date()})")

    # ─── 2. Lag / Rolling / EWMA / YoY features ───
    log.info("Adding lag features...")
    base = add_all_lag_features(
        base,
        target_cols=["Revenue", "COGS"],
        lag_days=cfg["lag_days"],
        rolling_windows=cfg["rolling_windows"],
        ewm_spans=cfg["ewm_spans"],
        date_col="Date",
    )

    # Ratio COGS/Revenue lag
    base["cogs_rev_ratio_lag7"] = (
        base["COGS"].shift(7) / (base["Revenue"].shift(7) + 1e-6)
    )
    base["cogs_rev_ratio_lag30"] = (
        base["COGS"].shift(30) / (base["Revenue"].shift(30) + 1e-6)
    )

    # ─── 3. Calendar features ───
    log.info("Adding calendar features...")
    base = add_calendar_features(base, date_col="Date")

    # ─── 4. Transactional features (lag 1 ngay) ───
    log.info("Building transactional aggregates...")
    daily_orders = build_daily_orders(orders, order_items, payments, customers, geography)
    daily_web    = build_daily_web_traffic(web_traffic)

    log.info("Joining transactional features (lag 1)...")
    base = add_lagged_transactional(base, daily_orders, lag=1)
    base = add_lagged_transactional(base, daily_web, lag=1)

    # ─── 5. Inventory features (forward-fill tu snapshot cuoi thang) ───
    log.info("Joining inventory features...")
    daily_inv = build_daily_inventory(inventory)
    # Forward fill: merge on nearest past snapshot
    base = pd.merge_asof(
        base.sort_values("Date"),
        daily_inv.sort_values("Date"),
        on="Date",
        direction="backward",
    )

    # ─── 6. Promotion features ───
    log.info("Building promotion features...")
    date_range = base["Date"]
    daily_promo = build_daily_promotions(promotions, date_range)
    base = base.merge(daily_promo, on="Date", how="left")

    # ─── 7. Derived / interaction features ───
    log.info("Adding derived features...")
    # Revenue momentum
    if "Revenue_lag7" in base.columns and "Revenue_lag14" in base.columns:
        base["rev_momentum_7_14"] = (
            base["Revenue_lag7"] / (base["Revenue_lag14"] + 1e-6)
        )
    if "Revenue_lag30" in base.columns and "Revenue_lag60" in base.columns:
        base["rev_momentum_30_60"] = (
            base["Revenue_lag30"] / (base["Revenue_lag60"] + 1e-6)
        )

    # Web * promo interaction
    if "total_sessions" in base.columns and "n_active_promos" in base.columns:
        base["sessions_x_promos"] = (
            base["total_sessions"].fillna(0) * base["n_active_promos"].fillna(0)
        )

    # Is growing (last 7 vs 30)
    if "Revenue_rmean7" in base.columns and "Revenue_rmean30" in base.columns:
        base["is_growing"] = (
            base["Revenue_rmean7"] > base["Revenue_rmean30"]
        ).astype(int)

    log.info(f"Feature matrix shape: {base.shape}")

    if save_path:
        base.to_parquet(save_path, index=False)
        log.info(f"Saved feature matrix to {save_path}")

    return base
