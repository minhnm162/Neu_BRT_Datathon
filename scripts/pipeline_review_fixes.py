from pathlib import Path
import json
import warnings

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline

warnings.filterwarnings("ignore")

try:
    from xgboost import XGBRegressor

    HAS_XGBOOST = True
except Exception:
    HAS_XGBOOST = False


RANDOM_SEED = 2026
DATE_CANDIDATE_COLUMNS = [
    "date",
    "Date",
    "order_date",
    "ship_date",
    "delivery_date",
    "return_date",
    "review_date",
    "signup_date",
    "snapshot_date",
    "start_date",
    "end_date",
]


def find_project_root() -> Path:
    return next(
        (candidate for candidate in [Path.cwd(), *Path.cwd().parents] if (candidate / "dataset").exists()),
        Path.cwd(),
    )


PROJECT_ROOT = find_project_root()
DATA_DIR = PROJECT_ROOT / "dataset"
DATA_UNDERSTANDING_DIR = PROJECT_ROOT / "artifacts" / "data_understanding"
FINAL_DIR = PROJECT_ROOT / "artifacts" / "final_submission"
AGG_DIR = PROJECT_ROOT / "aggregated_tables"

for directory in [DATA_UNDERSTANDING_DIR, FINAL_DIR, AGG_DIR]:
    directory.mkdir(parents=True, exist_ok=True)


def read_csv_table(path: Path) -> pd.DataFrame:
    header_cols = pd.read_csv(path, nrows=0).columns.tolist()
    parse_dates = [col for col in DATE_CANDIDATE_COLUMNS if col in header_cols]
    return pd.read_csv(path, parse_dates=parse_dates, low_memory=False)


def refresh_data_understanding_artifacts() -> dict:
    csv_paths = sorted(DATA_DIR.glob("*.csv"))
    dfs = {}
    load_rows = []

    for path in csv_paths:
        table = path.stem
        header_cols = pd.read_csv(path, nrows=0).columns.tolist()
        parse_dates = [col for col in DATE_CANDIDATE_COLUMNS if col in header_cols]
        df = pd.read_csv(path, parse_dates=parse_dates, low_memory=False)
        dfs[table] = df
        load_rows.append(
            {
                "table": table,
                "path": str(path.relative_to(PROJECT_ROOT)),
                "rows": len(df),
                "columns": len(df.columns),
                "parsed_date_columns": ", ".join(parse_dates) if parse_dates else "-",
            }
        )

    load_summary = pd.DataFrame(load_rows).sort_values("table").reset_index(drop=True)
    dataset_summary = pd.DataFrame(
        [
            {
                "table": table,
                "rows": len(df),
                "columns": len(df.columns),
                "column_names": ", ".join(df.columns),
            }
            for table, df in dfs.items()
        ]
    ).sort_values(["rows", "table"], ascending=[False, True])

    key_like_columns = {"zip", "date", "Date"}
    pk_rows = []
    for table, df in dfs.items():
        for col in df.columns:
            if not (col.endswith("_id") or col in key_like_columns):
                continue
            non_null = int(df[col].notna().sum())
            distinct = int(df[col].nunique(dropna=True))
            pk_rows.append(
                {
                    "table": table,
                    "column": col,
                    "row_count": len(df),
                    "non_null_rows": non_null,
                    "distinct_values": distinct,
                    "missing_rows": len(df) - non_null,
                    "uniqueness_ratio": round(distinct / len(df), 4) if len(df) else None,
                    "candidate_primary_key": (non_null == len(df)) and (distinct == len(df)),
                }
            )
    pk_df = pd.DataFrame(pk_rows).sort_values(
        ["candidate_primary_key", "table", "column"], ascending=[False, True, True]
    )

    fk_checks = [
        ("customers", "zip", "geography", "zip"),
        ("orders", "customer_id", "customers", "customer_id"),
        ("orders", "zip", "geography", "zip"),
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
        ("order_items", "promo_id", "promotions", "promo_id"),
        ("order_items", "promo_id_2", "promotions", "promo_id"),
        ("payments", "order_id", "orders", "order_id"),
        ("shipments", "order_id", "orders", "order_id"),
        ("returns", "order_id", "orders", "order_id"),
        ("returns", "product_id", "products", "product_id"),
        ("reviews", "order_id", "orders", "order_id"),
        ("reviews", "product_id", "products", "product_id"),
        ("reviews", "customer_id", "customers", "customer_id"),
        ("inventory", "product_id", "products", "product_id"),
    ]

    def infer_cardinality(left_df, left_key, right_df, right_key):
        left_unique = left_df[left_key].dropna().is_unique
        right_unique = right_df[right_key].dropna().is_unique
        if left_unique and right_unique:
            return "1:1"
        if left_unique and not right_unique:
            return "1:n"
        if not left_unique and right_unique:
            return "n:1"
        return "n:n"

    fk_rows = []
    for left_table, left_key, right_table, right_key in fk_checks:
        if left_table not in dfs or right_table not in dfs:
            continue
        left_df = dfs[left_table]
        right_keys = set(dfs[right_table][right_key].dropna().unique())
        non_null_left = left_df[left_key].dropna()
        unmatched = int((~non_null_left.isin(right_keys)).sum())
        fk_rows.append(
            {
                "left_table": left_table,
                "left_key": left_key,
                "right_table": right_table,
                "right_key": right_key,
                "checked_rows": len(left_df),
                "non_null_left_rows": len(non_null_left),
                "unmatched_rows": unmatched,
                "match_rate_pct": round((1 - unmatched / len(non_null_left)) * 100, 4) if len(non_null_left) else 100.0,
                "relationship": infer_cardinality(left_df, left_key, dfs[right_table], right_key),
                "note": "OK" if unmatched == 0 else "HAS_UNMATCHED_KEYS",
            }
        )
    fk_df = pd.DataFrame(fk_rows)
    join_map = fk_df[["left_table", "left_key", "right_table", "right_key", "relationship", "note"]].copy()

    missing_meaning = {
        ("order_items", "promo_id"): (
            "Business-valid null: item has no primary promotion. Do not fill with an arbitrary promo_id."
        ),
        ("order_items", "promo_id_2"): (
            "Business-valid null: item has no second/stacked promotion. Use an indicator if needed."
        ),
        ("promotions", "applicable_category"): (
            "Likely broad/all-category promotion metadata. Keep null or encode as broad_scope only after checking business question."
        ),
    }
    missing_rows = []
    for table, df in dfs.items():
        missing_count = df.isna().sum()
        missing_pct = (missing_count / len(df) * 100).round(2) if len(df) else missing_count
        for col in df.columns:
            if missing_count[col] <= 0:
                continue
            missing_rows.append(
                {
                    "table": table,
                    "column": col,
                    "missing_count": int(missing_count[col]),
                    "missing_pct": float(missing_pct[col]),
                    "business_interpretation": missing_meaning.get(
                        (table, col),
                        "Needs column-level business review before fill/drop.",
                    ),
                    "recommended_action": "Do not blanket-fill; handle only when required by the target analysis.",
                }
            )
    missing_df = pd.DataFrame(missing_rows)
    if not missing_df.empty:
        missing_df = missing_df.sort_values(["missing_pct", "missing_count", "table", "column"], ascending=[False, False, True, True])

    date_rows = []
    for table, df in dfs.items():
        date_cols = [col for col in df.columns if col in DATE_CANDIDATE_COLUMNS or pd.api.types.is_datetime64_any_dtype(df[col])]
        for col in date_cols:
            series = pd.to_datetime(df[col], errors="coerce").dropna()
            if series.empty:
                continue
            distinct_dates = series.dt.normalize().nunique()
            full_days = pd.date_range(series.min().normalize(), series.max().normalize(), freq="D")
            missing_days = len(set(full_days.date) - set(series.dt.date))
            date_rows.append(
                {
                    "table": table,
                    "date_column": col,
                    "min_date": series.min().date(),
                    "max_date": series.max().date(),
                    "distinct_dates": int(distinct_dates),
                    "missing_days_in_range": int(missing_days),
                }
            )
    date_ranges = pd.DataFrame(date_rows).sort_values(["table", "date_column"])

    table_usage = pd.DataFrame(
        [
            {"table": "customers", "MCQ": True, "EDA": True, "Forecasting": "Indirect", "future_availability": "historical dimension only", "reason": "Customer segmentation by age group, gender, and acquisition channel."},
            {"table": "geography", "MCQ": True, "EDA": True, "Forecasting": "Indirect", "future_availability": "static reference", "reason": "Reference table for city, district, and region joins."},
            {"table": "inventory", "MCQ": False, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future", "reason": "Monthly stock and stockout indicators are useful, but snapshot timing must be respected."},
            {"table": "order_items", "MCQ": True, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future", "reason": "Line-level quantity, price, discount, product, and promotion usage."},
            {"table": "orders", "MCQ": True, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future", "reason": "Core transaction table with order dates, channels, devices, status, and geography."},
            {"table": "payments", "MCQ": True, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future", "reason": "Payment method and installment mix support business analysis."},
            {"table": "products", "MCQ": True, "EDA": True, "Forecasting": "Indirect", "future_availability": "static reference", "reason": "Product dimension table for category, segment, size, price, and COGS."},
            {"table": "promotions", "MCQ": True, "EDA": True, "Forecasting": "Known calendar feature if provided", "future_availability": "known only for rows in promotions table", "reason": "Promotion calendar can be used if campaign dates are known without target leakage."},
            {"table": "returns", "MCQ": True, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future", "reason": "Return reasons and refund pressure explain net revenue risk."},
            {"table": "reviews", "MCQ": False, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future", "reason": "Ratings and review titles support customer-satisfaction analysis."},
            {"table": "sales", "MCQ": False, "EDA": True, "Forecasting": "Target train", "future_availability": "unknown target", "reason": "Training target table with Date, Revenue, and COGS."},
            {"table": "sample_submission", "MCQ": False, "EDA": False, "Forecasting": "Submission schema only", "future_availability": "future dates only", "reason": "Use only Date/order/schema. Ignore Revenue/COGS values to avoid leakage."},
            {"table": "shipments", "MCQ": False, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future", "reason": "Shipping delay and fee analysis for logistics insights."},
            {"table": "web_traffic", "MCQ": True, "EDA": True, "Forecasting": "Historical feature only", "future_availability": "not known for future unless provided separately", "reason": "Daily traffic can act as a demand signal only when using historical/lagged values."},
        ]
    )
    table_usage = table_usage[table_usage["table"].isin(dfs)].sort_values("table")

    exports = {
        "load_summary.csv": load_summary,
        "dataset_summary.csv": dataset_summary,
        "primary_key_profile.csv": pk_df,
        "foreign_key_profile.csv": fk_df,
        "join_map.csv": join_map,
        "missing_values.csv": missing_df,
        "date_ranges.csv": date_ranges,
        "table_usage.csv": table_usage,
    }
    for filename, df in exports.items():
        df.to_csv(DATA_UNDERSTANDING_DIR / filename, index=False, encoding="utf-8-sig")

    return dfs


def export_intermediate_tables(dfs: dict) -> None:
    orders = dfs["orders"]
    order_items = dfs["order_items"]
    products = dfs["products"]
    customers = dfs["customers"]
    geography = dfs["geography"]
    returns = dfs["returns"]
    inventory = dfs["inventory"]
    sales = dfs["sales"].rename(columns={"Date": "date"}).copy()

    order_lines = (
        order_items.merge(
            orders[["order_id", "order_date", "customer_id", "zip", "order_status", "payment_method", "device_type", "order_source"]],
            on="order_id",
            how="left",
        )
        .merge(products[["product_id", "product_name", "category", "segment", "size", "color", "price", "cogs"]], on="product_id", how="left")
        .merge(customers[["customer_id", "gender", "age_group", "acquisition_channel"]], on="customer_id", how="left")
        .merge(geography[["zip", "region", "district"]], on="zip", how="left")
    )
    order_lines["line_revenue"] = order_lines["quantity"] * order_lines["unit_price"]
    order_lines["line_revenue_after_discount"] = order_lines["line_revenue"] - order_lines["discount_amount"].fillna(0)
    order_lines["line_cogs"] = order_lines["quantity"] * order_lines["cogs"]
    order_lines["line_margin"] = order_lines["line_revenue_after_discount"] - order_lines["line_cogs"]
    order_lines.to_csv(AGG_DIR / "order_lines_enriched.csv", index=False, encoding="utf-8-sig")

    returns_enriched = (
        returns.merge(products[["product_id", "product_name", "category", "segment", "size", "color"]], on="product_id", how="left")
        .merge(orders[["order_id", "order_date", "customer_id", "order_status", "order_source", "device_type"]], on="order_id", how="left")
    )
    returns_enriched.to_csv(AGG_DIR / "returns_enriched.csv", index=False, encoding="utf-8-sig")

    inventory_monthly = (
        inventory.assign(month=inventory["snapshot_date"].dt.to_period("M").dt.to_timestamp())
        .groupby(["month", "category", "segment"], as_index=False)
        .agg(
            product_count=("product_id", "nunique"),
            stock_on_hand=("stock_on_hand", "sum"),
            units_received=("units_received", "sum"),
            units_sold=("units_sold", "sum"),
            stockout_days=("stockout_days", "sum"),
            avg_days_of_supply=("days_of_supply", "mean"),
            avg_fill_rate=("fill_rate", "mean"),
            stockout_flag_share=("stockout_flag", "mean"),
            overstock_flag_share=("overstock_flag", "mean"),
            reorder_flag_share=("reorder_flag", "mean"),
            avg_sell_through_rate=("sell_through_rate", "mean"),
        )
    )
    inventory_monthly.to_csv(AGG_DIR / "inventory_monthly_enriched.csv", index=False, encoding="utf-8-sig")

    daily_sales_features = build_feature_frame(
        dfs["sales"][["Date", "Revenue", "COGS"]].copy(),
        dfs["promotions"],
    ).rename(columns={"Date": "date"})
    daily_sales_features.to_csv(AGG_DIR / "daily_sales_features_final_grain.csv", index=False, encoding="utf-8-sig")

    table_grain = pd.DataFrame(
        [
            {"table": "order_lines_enriched.csv", "grain": "one row per order item line", "primary_use": "MCQ and EDA joins"},
            {"table": "returns_enriched.csv", "grain": "one row per return record", "primary_use": "EDA and return-pressure analysis"},
            {"table": "inventory_monthly_enriched.csv", "grain": "one row per month, category, segment", "primary_use": "inventory EDA"},
            {"table": "daily_sales_features_final_grain.csv", "grain": "one row per date", "primary_use": "forecasting feature audit"},
        ]
    )
    table_grain.to_csv(AGG_DIR / "table_grain_map.csv", index=False, encoding="utf-8-sig")

    daily_check = sales.merge(
        order_lines.groupby("order_date", as_index=False).agg(line_revenue=("line_revenue", "sum")),
        left_on="date",
        right_on="order_date",
        how="left",
    )
    daily_check["revenue_matches_order_lines"] = np.isclose(daily_check["Revenue"], daily_check["line_revenue"])
    pd.DataFrame(
        [
            {
                "checked_days": len(daily_check),
                "matching_days": int(daily_check["revenue_matches_order_lines"].sum()),
                "all_days_match": bool(daily_check["revenue_matches_order_lines"].all()),
                "note": "sales.Revenue equals sum(quantity * unit_price) by order_date in the current data.",
            }
        ]
    ).to_csv(AGG_DIR / "daily_sales_reconciliation.csv", index=False, encoding="utf-8-sig")


def make_promo_daily(all_dates: pd.DataFrame, promotions_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for row in promotions_df.itertuples(index=False):
        start = getattr(row, "start_date")
        end = getattr(row, "end_date")
        if pd.notna(start) and pd.notna(end):
            active_dates = pd.date_range(start, end, freq="D")
            rows.append(
                pd.DataFrame(
                    {
                        "Date": active_dates,
                        "promo_id": getattr(row, "promo_id"),
                        "promo_type": getattr(row, "promo_type"),
                        "promo_channel": getattr(row, "promo_channel"),
                        "applicable_category": getattr(row, "applicable_category"),
                    }
                )
            )
    if rows:
        raw = pd.concat(rows, ignore_index=True)
        daily = raw.groupby("Date", as_index=False).agg(
            active_campaigns=("promo_id", "nunique"),
            active_promo_types=("promo_type", "nunique"),
            active_promo_channels=("promo_channel", "nunique"),
            active_promo_categories=("applicable_category", "nunique"),
        )
    else:
        daily = pd.DataFrame(columns=["Date", "active_campaigns", "active_promo_types", "active_promo_channels", "active_promo_categories"])
    return all_dates.merge(daily, on="Date", how="left").fillna(0)


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["day_of_week"] = out["Date"].dt.dayofweek
    out["day_of_month"] = out["Date"].dt.day
    out["day_of_year"] = out["Date"].dt.dayofyear
    out["week_of_year"] = out["Date"].dt.isocalendar().week.astype(int)
    out["month"] = out["Date"].dt.month
    out["quarter"] = out["Date"].dt.quarter
    out["year"] = out["Date"].dt.year
    out["is_weekend"] = out["day_of_week"].isin([5, 6]).astype(int)
    out["time_index"] = np.arange(len(out))
    return out


def add_lag_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    revenue_past = out["Revenue"].shift(1)
    cogs_past = out["COGS"].shift(1)
    for lag in [1, 7, 14, 28, 30, 60, 90, 365]:
        out[f"revenue_lag_{lag}"] = out["Revenue"].shift(lag)
        out[f"cogs_lag_{lag}"] = out["COGS"].shift(lag)
    for window in [7, 14, 28, 30, 60, 90]:
        out[f"revenue_roll_mean_{window}"] = revenue_past.rolling(window, min_periods=max(2, window // 3)).mean()
        out[f"revenue_roll_std_{window}"] = revenue_past.rolling(window, min_periods=max(2, window // 3)).std()
        out[f"cogs_roll_mean_{window}"] = cogs_past.rolling(window, min_periods=max(2, window // 3)).mean()
    out["revenue_ewm_7"] = revenue_past.ewm(span=7, adjust=False).mean()
    out["revenue_ewm_30"] = revenue_past.ewm(span=30, adjust=False).mean()
    return out


def build_feature_frame(history_df: pd.DataFrame, promotions_df: pd.DataFrame, future_dates=None) -> pd.DataFrame:
    history = history_df[["Date", "Revenue", "COGS"]].sort_values("Date").copy()
    if future_dates is not None:
        future = pd.DataFrame({"Date": pd.to_datetime(future_dates)})
        future["Revenue"] = np.nan
        future["COGS"] = np.nan
        combined = pd.concat([history, future], ignore_index=True).sort_values("Date").reset_index(drop=True)
    else:
        combined = history.reset_index(drop=True)
    combined = add_calendar_features(combined)
    combined = add_lag_rolling_features(combined)
    promo_features = make_promo_daily(combined[["Date"]], promotions_df)
    return combined.merge(promo_features, on="Date", how="left")


def make_model():
    if HAS_XGBOOST:
        return Pipeline(
            steps=[
                ("imputer", SimpleImputer(strategy="median")),
                (
                    "model",
                    XGBRegressor(
                        n_estimators=600,
                        max_depth=4,
                        learning_rate=0.03,
                        subsample=0.90,
                        colsample_bytree=0.90,
                        objective="reg:squarederror",
                        random_state=RANDOM_SEED,
                        n_jobs=4,
                    ),
                ),
            ]
        )
    return Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            (
                "model",
                RandomForestRegressor(
                    n_estimators=400,
                    max_depth=14,
                    min_samples_leaf=4,
                    random_state=RANDOM_SEED,
                    n_jobs=-1,
                ),
            ),
        ]
    )


def metric_row(y_true, y_pred, target, model_family, validation_mode):
    return {
        "target": target,
        "model": model_family,
        "validation_mode": validation_mode,
        "MAE": mean_absolute_error(y_true, y_pred),
        "RMSE": np.sqrt(mean_squared_error(y_true, y_pred)),
        "R2": r2_score(y_true, y_pred),
    }


def run_recursive_backtest(dfs: dict) -> None:
    sales = dfs["sales"][["Date", "Revenue", "COGS"]].sort_values("Date").reset_index(drop=True)
    promotions = dfs["promotions"]
    validation_start = pd.Timestamp("2022-01-01")
    validation_end = sales["Date"].max()

    full_feature_frame = build_feature_frame(sales, promotions)
    feature_cols = [c for c in full_feature_frame.columns if c not in ["Date", "Revenue", "COGS"]]
    model_frame = full_feature_frame.dropna(subset=["Revenue", "COGS", "revenue_lag_365", "revenue_roll_mean_90"]).copy()
    train_frame = model_frame[model_frame["Date"] < validation_start].copy()
    valid_frame = model_frame[(model_frame["Date"] >= validation_start) & (model_frame["Date"] <= validation_end)].copy()

    model_family = "xgboost" if HAS_XGBOOST else "random_forest"
    revenue_model = make_model()
    cogs_model = make_model()
    revenue_model.fit(train_frame[feature_cols], train_frame["Revenue"])
    cogs_model.fit(train_frame[feature_cols], train_frame["COGS"])

    teacher_revenue = revenue_model.predict(valid_frame[feature_cols])
    teacher_cogs = cogs_model.predict(valid_frame[feature_cols])

    history = sales[sales["Date"] < validation_start][["Date", "Revenue", "COGS"]].copy().reset_index(drop=True)
    actual_validation = sales[(sales["Date"] >= validation_start) & (sales["Date"] <= validation_end)].copy()
    prediction_rows = []

    for current_date in actual_validation["Date"].tolist():
        frame = build_feature_frame(history, promotions, [current_date])
        row = frame[frame["Date"] == current_date].tail(1)
        pred_revenue = max(float(revenue_model.predict(row[feature_cols])[0]), 0.0)
        pred_cogs = max(float(cogs_model.predict(row[feature_cols])[0]), 0.0)
        actual_row = actual_validation.loc[actual_validation["Date"] == current_date].iloc[0]
        prediction_rows.append(
            {
                "Date": current_date,
                "Revenue_actual": actual_row["Revenue"],
                "COGS_actual": actual_row["COGS"],
                "Revenue_pred_recursive": pred_revenue,
                "COGS_pred_recursive": pred_cogs,
            }
        )
        history = pd.concat(
            [
                history,
                pd.DataFrame([{"Date": current_date, "Revenue": pred_revenue, "COGS": pred_cogs}]),
            ],
            ignore_index=True,
        )

    recursive_predictions = pd.DataFrame(prediction_rows)
    recursive_predictions["Revenue_residual"] = recursive_predictions["Revenue_actual"] - recursive_predictions["Revenue_pred_recursive"]
    recursive_predictions["COGS_residual"] = recursive_predictions["COGS_actual"] - recursive_predictions["COGS_pred_recursive"]

    scores = pd.DataFrame(
        [
            metric_row(valid_frame["Revenue"], teacher_revenue, "Revenue", model_family, "teacher_forcing_one_step"),
            metric_row(valid_frame["COGS"], teacher_cogs, "COGS", model_family, "teacher_forcing_one_step"),
            metric_row(
                recursive_predictions["Revenue_actual"],
                recursive_predictions["Revenue_pred_recursive"],
                "Revenue",
                model_family,
                "recursive_walk_forward",
            ),
            metric_row(
                recursive_predictions["COGS_actual"],
                recursive_predictions["COGS_pred_recursive"],
                "COGS",
                model_family,
                "recursive_walk_forward",
            ),
        ]
    )

    recursive_predictions.to_csv(FINAL_DIR / "recursive_backtest_2022_predictions.csv", index=False, encoding="utf-8-sig")
    scores.to_csv(FINAL_DIR / "recursive_backtest_2022_scores.csv", index=False, encoding="utf-8-sig")

    config_path = FINAL_DIR / "final_pipeline_config.json"
    config = json.loads(config_path.read_text(encoding="utf-8")) if config_path.exists() else {}
    config["recursive_backtest"] = {
        "validation_start": str(validation_start.date()),
        "validation_end": str(validation_end.date()),
        "rows": int(len(recursive_predictions)),
        "score_file": "artifacts/final_submission/recursive_backtest_2022_scores.csv",
        "prediction_file": "artifacts/final_submission/recursive_backtest_2022_predictions.csv",
        "note": "This walk-forward score mimics the recursive submission horizon better than one-step validation.",
    }
    leakage_controls = config.get("leakage_controls", [])
    extra_control = "2022 validation also evaluated with recursive walk-forward predictions"
    if extra_control not in leakage_controls:
        leakage_controls.append(extra_control)
    config["leakage_controls"] = leakage_controls
    config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")


def main() -> None:
    dfs = refresh_data_understanding_artifacts()
    export_intermediate_tables(dfs)
    run_recursive_backtest(dfs)
    print("Refreshed data understanding artifacts:", DATA_UNDERSTANDING_DIR)
    print("Exported intermediate tables:", AGG_DIR)
    print("Saved recursive backtest artifacts:", FINAL_DIR)


if __name__ == "__main__":
    main()
