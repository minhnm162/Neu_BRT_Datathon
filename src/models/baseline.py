"""Baseline models: Naive, SeasonalNaive (lag 365), EMA."""
import numpy as np
import pandas as pd


class NaiveModel:
    """Predict = gia tri ngay truoc (lag 1)."""
    def __init__(self):
        self.last_value = None

    def fit(self, dates, values):
        self.last_value = values[-1]
        self._series = pd.Series(values, index=dates)
        return self

    def predict_series(self, dates):
        preds = []
        series = self._series.copy()
        for d in sorted(dates):
            prev = series.get(d - pd.Timedelta(days=1), self.last_value)
            preds.append(prev)
        return np.array(preds)


class SeasonalNaiveModel:
    """Predict = gia tri cung ngay nam truoc (lag 365)."""
    def __init__(self, season: int = 365):
        self.season = season
        self._series = None

    def fit(self, dates, values):
        self._series = pd.Series(values, index=pd.to_datetime(dates))
        return self

    def predict_series(self, dates):
        preds = []
        for d in sorted(pd.to_datetime(dates)):
            lag_date = d - pd.Timedelta(days=self.season)
            val = self._series.get(lag_date, np.nan)
            if np.isnan(val):
                # fallback: tim ngay gan nhat trong window +-3 ngay
                candidates = [self._series.get(lag_date + pd.Timedelta(days=k), np.nan)
                               for k in range(-3, 4)]
                candidates = [v for v in candidates if not np.isnan(v)]
                val = np.mean(candidates) if candidates else self._series.mean()
            preds.append(val)
        return np.array(preds)


class EMAModel:
    """Exponentially weighted moving average."""
    def __init__(self, span: int = 30):
        self.span = span
        self._series = None
        self._last_ema = None

    def fit(self, dates, values):
        s = pd.Series(values, index=pd.to_datetime(dates))
        self._series = s
        self._last_ema = s.ewm(span=self.span).mean().iloc[-1]
        return self

    def predict_series(self, dates):
        alpha = 2 / (self.span + 1)
        ema = self._last_ema
        preds = []
        for _ in sorted(dates):
            preds.append(ema)
        return np.array(preds)


class COGSRatioModel:
    """Du bao COGS = Revenue_pred * rolling_ratio."""
    def __init__(self, window: int = 90):
        self.window = window
        self._ratio = None

    def fit(self, revenue: pd.Series, cogs: pd.Series):
        ratio_series = cogs / (revenue + 1e-6)
        self._ratio  = ratio_series.rolling(self.window, min_periods=30).mean().iloc[-1]
        return self

    def predict(self, revenue_pred: np.ndarray) -> np.ndarray:
        return revenue_pred * self._ratio
