"""
Calendar features: ngay thang, mua vu, le Viet Nam, Tet Nguyen Dan, Fourier.
Tat ca features chi dung thong tin cua chinh ngay D (khong look-ahead).
"""
import numpy as np
import pandas as pd
from typing import Optional


# ─── Tet Nguyen Dan (Am lich 1/1) - lich duong tuong ung ───
TET_DATES = {
    2012: "2012-01-23", 2013: "2013-02-10", 2014: "2014-01-31",
    2015: "2015-02-19", 2016: "2016-02-08", 2017: "2017-01-28",
    2018: "2018-02-16", 2019: "2019-02-05", 2020: "2020-01-25",
    2021: "2021-02-12", 2022: "2022-02-01", 2023: "2023-01-22",
    2024: "2024-02-10", 2025: "2025-01-29",
}

# Le Viet Nam chinh thuc (thang-ngay)
VN_HOLIDAYS_FIXED = [
    (1, 1),   # Tet Duong lich
    (4, 30),  # Giai phong
    (5, 1),   # Lao dong
    (9, 2),   # Quoc khanh
]

# Shopping events quan trong
SHOPPING_EVENTS = {
    "11_11": (11, 11),
    "12_12": (12, 12),
    "black_friday": None,  # Thu 6 cuoi cung cua thang 11
    "christmas_eve": (12, 24),
    "christmas": (12, 25),
    "new_year_eve": (12, 31),
    "valentine": (2, 14),
    "womens_day": (3, 8),
    "mid_autumn": None,    # 15/8 Am lich - xu ly rieng neu can
}


def _tet_day(year: int) -> Optional[pd.Timestamp]:
    return pd.Timestamp(TET_DATES[year]) if year in TET_DATES else None


def add_calendar_features(df: pd.DataFrame, date_col: str = "Date") -> pd.DataFrame:
    """
    Them tat ca calendar features vao df.
    df phai co cot date_col kieu datetime.
    """
    d = df.copy()
    dt = d[date_col]

    # --- Basic ---
    d["year"]         = dt.dt.year
    d["month"]        = dt.dt.month
    d["day"]          = dt.dt.day
    d["dow"]          = dt.dt.dayofweek          # 0=Mon
    d["doy"]          = dt.dt.dayofyear
    d["week"]         = dt.dt.isocalendar().week.astype(int)
    d["quarter"]      = dt.dt.quarter
    d["is_weekend"]   = (dt.dt.dayofweek >= 5).astype(int)
    d["is_month_start"] = dt.dt.is_month_start.astype(int)
    d["is_month_end"]   = dt.dt.is_month_end.astype(int)
    d["is_quarter_start"] = dt.dt.is_quarter_start.astype(int)
    d["is_quarter_end"]   = dt.dt.is_quarter_end.astype(int)
    d["days_in_month"]  = dt.dt.days_in_month

    # --- Payday (15 va cuoi thang) ---
    d["is_payday"] = ((d["day"] == 15) | (d["is_month_end"] == 1)).astype(int)

    # --- Le Viet Nam co dinh ---
    d["is_vn_holiday"] = d.apply(
        lambda r: int((r[date_col].month, r[date_col].day) in VN_HOLIDAYS_FIXED), axis=1
    )

    # --- Tet Nguyen Dan window ---
    def tet_features(row):
        yr  = row[date_col].year
        tet = _tet_day(yr)
        tet_prev = _tet_day(yr - 1)
        tet_next = _tet_day(yr + 1)

        # Tim Tet gan nhat
        candidates = [t for t in [tet, tet_prev, tet_next] if t is not None]
        deltas = [(row[date_col] - t).days for t in candidates]
        closest_idx = np.argmin(np.abs(deltas))
        delta = deltas[closest_idx]
        closest = candidates[closest_idx]

        days_to_tet   = max(0, -delta)   # So ngay truoc Tet
        days_after_tet = max(0, delta)   # So ngay sau Tet
        is_tet_window  = int(-15 <= delta <= 20)
        is_tet_eve     = int(-3 <= delta <= 0)
        is_tet_holiday = int(0 <= delta <= 7)
        return pd.Series({
            "days_to_tet":    days_to_tet,
            "days_after_tet": days_after_tet,
            "is_tet_window":  is_tet_window,
            "is_tet_eve":     is_tet_eve,
            "is_tet_holiday": is_tet_holiday,
        })

    tet_feats = d[[date_col]].apply(tet_features, axis=1)
    d = pd.concat([d, tet_feats], axis=1)

    # --- Shopping events co dinh ---
    d["is_1111"]        = ((d["month"] == 11) & (d["day"] == 11)).astype(int)
    d["is_1212"]        = ((d["month"] == 12) & (d["day"] == 12)).astype(int)
    d["is_christmas"]   = ((d["month"] == 12) & (d["day"].isin([24, 25]))).astype(int)
    d["is_valentine"]   = ((d["month"] == 2) & (d["day"] == 14)).astype(int)
    d["is_womens_day"]  = ((d["month"] == 3) & (d["day"] == 8)).astype(int)
    d["is_new_year_eve"] = ((d["month"] == 12) & (d["day"] == 31)).astype(int)
    d["is_labor_day"]   = ((d["month"] == 5) & (d["day"] == 1)).astype(int)
    d["is_national_day"] = ((d["month"] == 9) & (d["day"] == 2)).astype(int)

    # Black Friday = Thu 6 cuoi cung thang 11
    def is_black_friday(row):
        m, dow = row[date_col].month, row[date_col].dayofweek
        if m != 11 or dow != 4:  # 4=Friday
            return 0
        # Check ngay nay co phai Thu 6 cuoi cung thang 11 khong
        last_day = pd.Timestamp(row[date_col].year, 11, 30)
        # Tim Thu 6 cuoi: offset ngay cuoi - 6 + (4-weekday(last_day))%7
        last_fri = last_day - pd.Timedelta(days=(last_day.dayofweek - 4) % 7)
        return int(row[date_col] == last_fri)

    d["is_black_friday"] = d[[date_col]].apply(is_black_friday, axis=1)

    # --- Fourier seasonality ---
    # Weekly (chu ky 7 ngay)
    for k in range(1, 4):
        d[f"fourier_w_sin_{k}"] = np.sin(2 * np.pi * k * d["dow"] / 7)
        d[f"fourier_w_cos_{k}"] = np.cos(2 * np.pi * k * d["dow"] / 7)
    # Yearly (chu ky 365.25 ngay)
    for k in range(1, 11):
        d[f"fourier_y_sin_{k}"] = np.sin(2 * np.pi * k * d["doy"] / 365.25)
        d[f"fourier_y_cos_{k}"] = np.cos(2 * np.pi * k * d["doy"] / 365.25)

    # Trend (time index chuan hoa)
    min_date = dt.min()
    d["trend"] = (dt - min_date).dt.days
    d["trend_sq"] = d["trend"] ** 2

    return d
