"""
Lag / rolling / EWMA features cho target (Revenue, COGS).
Tat ca features duoc tinh tren history <= D-1, khong look-ahead.
"""
import numpy as np
import pandas as pd
from typing import List


def add_lag_features(df: pd.DataFrame,
                     target_col: str,
                     lag_days: List[int],
                     date_col: str = "Date") -> pd.DataFrame:
    """Them cac lag features."""
    d = df.sort_values(date_col).copy()
    for lag in lag_days:
        d[f"{target_col}_lag{lag}"] = d[target_col].shift(lag)
    return d


def add_rolling_features(df: pd.DataFrame,
                         target_col: str,
                         windows: List[int],
                         date_col: str = "Date") -> pd.DataFrame:
    """Them rolling mean/median/std/min/max."""
    d = df.sort_values(date_col).copy()
    for w in windows:
        shifted = d[target_col].shift(1)  # Shift 1 de tranh leakage
        d[f"{target_col}_rmean{w}"]   = shifted.rolling(w, min_periods=1).mean()
        d[f"{target_col}_rmedian{w}"] = shifted.rolling(w, min_periods=1).median()
        d[f"{target_col}_rstd{w}"]    = shifted.rolling(w, min_periods=2).std().fillna(0)
        d[f"{target_col}_rmin{w}"]    = shifted.rolling(w, min_periods=1).min()
        d[f"{target_col}_rmax{w}"]    = shifted.rolling(w, min_periods=1).max()
    return d


def add_ewm_features(df: pd.DataFrame,
                     target_col: str,
                     spans: List[int],
                     date_col: str = "Date") -> pd.DataFrame:
    """Them Exponentially Weighted Moving Average features."""
    d = df.sort_values(date_col).copy()
    shifted = d[target_col].shift(1)
    for span in spans:
        d[f"{target_col}_ewm{span}"] = shifted.ewm(span=span, adjust=False).mean()
    return d


def add_yoy_features(df: pd.DataFrame,
                     target_col: str,
                     date_col: str = "Date") -> pd.DataFrame:
    """Year-over-Year ratio va diff."""
    d = df.sort_values(date_col).copy()
    lag365 = d[target_col].shift(365)
    lag364 = d[target_col].shift(364)
    lag366 = d[target_col].shift(366)

    d[f"{target_col}_lag365"]    = lag365
    d[f"{target_col}_yoy_ratio"] = d[target_col].shift(1) / (lag365 + 1e-6)
    d[f"{target_col}_yoy_diff"]  = d[target_col].shift(1) - lag365

    # Same week last year (trung binh 3 ngay quanh lag 364)
    d[f"{target_col}_same_week_ly"] = (lag364 + lag365 + lag366) / 3
    return d


def add_all_lag_features(df: pd.DataFrame,
                         target_cols: List[str],
                         lag_days: List[int],
                         rolling_windows: List[int],
                         ewm_spans: List[int],
                         date_col: str = "Date") -> pd.DataFrame:
    """Pipeline tong hop tat ca lag/rolling/ewm/yoy cho nhieu cot target."""
    d = df.copy()
    for col in target_cols:
        d = add_lag_features(d, col, lag_days, date_col)
        d = add_rolling_features(d, col, rolling_windows, date_col)
        d = add_ewm_features(d, col, ewm_spans, date_col)
        d = add_yoy_features(d, col, date_col)
    return d
