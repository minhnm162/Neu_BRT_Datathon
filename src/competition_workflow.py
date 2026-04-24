from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import pandas as pd


DATE_CANDIDATE_COLUMNS = (
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
)

EXCLUDED_DATASET_TABLES = {"sample_submission", "submission"}

JOIN_MAP_ROWS = [
    {"source_table": "orders", "join_key": "order_id", "related_table": "order_items", "note": "1:N"},
    {"source_table": "orders", "join_key": "order_id", "related_table": "shipments", "note": "1:N"},
    {"source_table": "orders", "join_key": "order_id", "related_table": "payments", "note": "1:N"},
    {"source_table": "orders", "join_key": "order_id", "related_table": "reviews", "note": "1:N"},
    {"source_table": "orders", "join_key": "customer_id", "related_table": "customers", "note": "N:1"},
    {"source_table": "order_items", "join_key": "product_id", "related_table": "products", "note": "N:1"},
    {"source_table": "order_items", "join_key": "product_id", "related_table": "inventory", "note": "N:1"},
    {"source_table": "order_items", "join_key": "promo_id", "related_table": "promotions", "note": "N:1, nullable"},
    {"source_table": "orders", "join_key": "order_id", "related_table": "returns", "note": "1:1 or null"},
    {"source_table": "customers", "join_key": "geography_id", "related_table": "geography", "note": "N:1"},
    {"source_table": "sales", "join_key": "Date", "related_table": "web_traffic", "note": "Temporal join by date"},
]

TABLE_USAGE_ROWS = [
    {"table": "orders", "mcq": True, "eda": True, "forecasting": True},
    {"table": "order_items", "mcq": True, "eda": True, "forecasting": True},
    {"table": "products", "mcq": True, "eda": True, "forecasting": False},
    {"table": "customers", "mcq": True, "eda": True, "forecasting": False},
    {"table": "geography", "mcq": True, "eda": True, "forecasting": False},
    {"table": "returns", "mcq": True, "eda": True, "forecasting": True},
    {"table": "reviews", "mcq": False, "eda": True, "forecasting": True},
    {"table": "shipments", "mcq": False, "eda": True, "forecasting": True},
    {"table": "inventory", "mcq": False, "eda": True, "forecasting": True},
    {"table": "web_traffic", "mcq": True, "eda": True, "forecasting": True},
    {"table": "promotions", "mcq": True, "eda": True, "forecasting": True},
    {"table": "sales", "mcq": False, "eda": True, "forecasting": True},
    {"table": "payments", "mcq": True, "eda": False, "forecasting": False},
]

EDA_THEME_PLAN_ROWS = [
    {
        "theme": "Theme 1 - Revenue & Demand",
        "business_question": "Revenue changes over time and the strongest product/category demand drivers.",
        "tables_needed": "sales, orders, order_items, products",
        "primary_metrics": "Monthly revenue, YoY growth, category share, AOV",
        "recommended_charts": "Time-series line, seasonality heatmap, stacked category bars, net revenue ranking",
        "expected_insight": "Identify peak periods and the categories or segments carrying the topline.",
        "recommendation": "Shift inventory and campaign budget toward peak windows and top categories.",
    },
    {
        "theme": "Theme 2 - Customer & Channel",
        "business_question": "Which channels, devices, and regions drive efficient conversion and repeat demand?",
        "tables_needed": "web_traffic, orders, customers, geography",
        "primary_metrics": "Bounce rate, session-to-order rate, orders per customer, revenue by region",
        "recommended_charts": "Bounce-rate bar, source scatter, device mix bar, revenue by region bar/map",
        "expected_insight": "Find low-quality traffic sources and the channel-region combinations worth scaling.",
        "recommendation": "Reallocate spend toward efficient sources and reinforce high-performing regions.",
    },
    {
        "theme": "Theme 3 - Returns & Customer Experience",
        "business_question": "Which products drive returns and how do logistics affect customer satisfaction?",
        "tables_needed": "returns, order_items, products, reviews, shipments",
        "primary_metrics": "Return rate, return reasons, average rating, refund amount, shipping delay",
        "recommended_charts": "Return heatmap, return-reason bar, delay-rating scatter, rating box plot",
        "expected_insight": "Detect fit, quality, or fulfillment issues that increase churn risk.",
        "recommendation": "Improve size guidance, tighten logistics SLAs, and prioritize problematic SKUs.",
    },
    {
        "theme": "Theme 4 - Inventory & Operations",
        "business_question": "Where are stockouts or overstock reducing revenue efficiency?",
        "tables_needed": "inventory, order_items, products, sales",
        "primary_metrics": "Stockout days, fill rate, sell-through rate, lost revenue estimate",
        "recommended_charts": "Stockout bar, fill-rate heatmap, sell-through ranking, lost-revenue bar",
        "expected_insight": "Quantify operational bottlenecks and the categories most exposed to stock risk.",
        "recommendation": "Raise safety stock for constrained categories and unwind persistent overstock.",
    },
]

EDA_CHART_PLAN_ROWS = [
    {"theme": "Theme 1", "chart_name": "Monthly revenue trend", "chart_type": "line", "grain": "month", "output_file": "charts/theme1_monthly_revenue.png"},
    {"theme": "Theme 1", "chart_name": "Revenue seasonality matrix", "chart_type": "heatmap", "grain": "month x year", "output_file": "charts/theme1_revenue_seasonality.png"},
    {"theme": "Theme 1", "chart_name": "Quarterly category contribution", "chart_type": "stacked bar", "grain": "quarter x category", "output_file": "charts/theme1_category_contribution.png"},
    {"theme": "Theme 1", "chart_name": "Top segments by net revenue", "chart_type": "bar", "grain": "segment", "output_file": "charts/theme1_segment_net_revenue.png"},
    {"theme": "Theme 2", "chart_name": "Bounce rate by traffic source", "chart_type": "bar", "grain": "traffic_source", "output_file": "charts/theme2_bounce_rate_by_source.png"},
    {"theme": "Theme 2", "chart_name": "Sessions vs orders by source", "chart_type": "scatter", "grain": "traffic_source", "output_file": "charts/theme2_sessions_vs_orders.png"},
    {"theme": "Theme 2", "chart_name": "Order count by device type", "chart_type": "bar", "grain": "device_type", "output_file": "charts/theme2_orders_by_device.png"},
    {"theme": "Theme 2", "chart_name": "Revenue by region", "chart_type": "bar", "grain": "region", "output_file": "charts/theme2_revenue_by_region.png"},
    {"theme": "Theme 3", "chart_name": "Return rate by size and category", "chart_type": "heatmap", "grain": "size x category", "output_file": "charts/theme3_return_rate_heatmap.png"},
    {"theme": "Theme 3", "chart_name": "Return reasons for Streetwear vs other segments", "chart_type": "bar", "grain": "return_reason", "output_file": "charts/theme3_return_reasons.png"},
    {"theme": "Theme 3", "chart_name": "Shipping delay vs review rating", "chart_type": "scatter", "grain": "order", "output_file": "charts/theme3_delay_vs_rating.png"},
    {"theme": "Theme 3", "chart_name": "Review rating by category", "chart_type": "box", "grain": "category", "output_file": "charts/theme3_rating_by_category.png"},
    {"theme": "Theme 4", "chart_name": "Stockout days by category", "chart_type": "bar", "grain": "category", "output_file": "charts/theme4_stockout_days.png"},
    {"theme": "Theme 4", "chart_name": "Fill rate by category and month", "chart_type": "heatmap", "grain": "category x month", "output_file": "charts/theme4_fill_rate_heatmap.png"},
    {"theme": "Theme 4", "chart_name": "Sell-through rate by category", "chart_type": "bar", "grain": "category", "output_file": "charts/theme4_sell_through.png"},
    {"theme": "Theme 4", "chart_name": "Estimated lost revenue by category", "chart_type": "bar", "grain": "category", "output_file": "charts/theme4_lost_revenue.png"},
]

EDA_JOIN_PREP_ROWS = [
    {"theme": "Theme 1", "join_instruction": "Join order_items to orders on order_id, then enrich with products on product_id."},
    {"theme": "Theme 1", "join_instruction": "Use sales as the authoritative daily target table for revenue and COGS."},
    {"theme": "Theme 2", "join_instruction": "Join orders to customers on customer_id and geography on zip."},
    {"theme": "Theme 2", "join_instruction": "Aggregate web_traffic by date and traffic_source before channel comparison."},
    {"theme": "Theme 3", "join_instruction": "Join returns to order_items and products on order_id + product_id to recover size and segment."},
    {"theme": "Theme 3", "join_instruction": "Join reviews and shipments on order_id to compute delay-rating relationships."},
    {"theme": "Theme 4", "join_instruction": "Use inventory snapshot_date monthly aggregates and enrich with products when needed."},
    {"theme": "Theme 4", "join_instruction": "Estimate lost revenue by combining inventory stockout exposure with realized category revenue."},
]

INSIGHT_TAXONOMY_ROWS = [
    {"insight": "Revenue seasonality peaks in Q4", "tier": "Descriptive", "priority": 1},
    {"insight": "A traffic source has high sessions but weak conversion efficiency", "tier": "Diagnostic", "priority": 2},
    {"insight": "Specific sizes or segments carry outsized return rates", "tier": "Diagnostic", "priority": 2},
    {"insight": "Stockouts suppress potential category revenue", "tier": "Diagnostic", "priority": 3},
    {"insight": "Lower shipping delay is associated with higher customer ratings", "tier": "Predictive", "priority": 4},
    {"insight": "Budget reallocation toward efficient channels can improve ROI", "tier": "Prescriptive", "priority": 5},
]

MCQ_PROMPTS = {
    "Q1": "What is the typical inter-order gap by customer?",
    "Q2": "Which segment has the highest gross margin percentage?",
    "Q3": "What is the most common return reason for Streetwear?",
    "Q4": "Which traffic source has the lowest average bounce rate?",
    "Q5": "What share of order-item rows use at least one promotion?",
    "Q6": "Which age group has the highest average order count per customer?",
    "Q7": "Which region generates the highest estimated revenue?",
    "Q8": "Which payment method is most common among cancelled orders?",
    "Q9": "Which size has the highest return rate?",
    "Q10": "Which installment count has the highest average payment value?",
}


def _singularize(table_name: str) -> str:
    if table_name.endswith("ies"):
        return table_name[:-3] + "y"
    if table_name.endswith("s"):
        return table_name[:-1]
    return table_name


def infer_date_columns(csv_path: Path) -> list[str]:
    header_cols = pd.read_csv(csv_path, nrows=0).columns.tolist()
    return [column for column in DATE_CANDIDATE_COLUMNS if column in header_cols]


def load_tables(dataset_dir: str | Path) -> dict[str, pd.DataFrame]:
    dataset_path = Path(dataset_dir)
    tables: dict[str, pd.DataFrame] = {}

    for csv_path in sorted(dataset_path.glob("*.csv")):
        if csv_path.stem in EXCLUDED_DATASET_TABLES:
            continue
        parse_dates = infer_date_columns(csv_path)
        tables[csv_path.stem] = pd.read_csv(
            csv_path,
            parse_dates=parse_dates,
            low_memory=False,
        )

    return tables


def find_date_columns(df: pd.DataFrame) -> list[str]:
    return [
        column
        for column in df.columns
        if pd.api.types.is_datetime64_any_dtype(df[column])
    ]


def guess_primary_key(table_name: str, columns: Iterable[str]) -> str | None:
    columns = list(columns)
    singular = _singularize(table_name)
    candidates = [
        f"{table_name}_id",
        f"{singular}_id",
        "id",
    ]

    for candidate in candidates:
        if candidate in columns:
            return candidate

    id_like_columns = [column for column in columns if column.endswith("_id")]
    if len(id_like_columns) == 1:
        return id_like_columns[0]

    return None


def format_date_ranges(df: pd.DataFrame) -> str:
    ranges: list[str] = []
    for column in find_date_columns(df):
        non_null = df[column].dropna()
        if non_null.empty:
            continue
        start = non_null.min()
        end = non_null.max()
        start_label = start.strftime("%Y-%m-%d") if hasattr(start, "strftime") else str(start)
        end_label = end.strftime("%Y-%m-%d") if hasattr(end, "strftime") else str(end)
        ranges.append(f"{column}: {start_label} -> {end_label}")
    return " | ".join(ranges) if ranges else "-"


def build_dataset_summary(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows: list[dict[str, object]] = []

    for table_name, df in sorted(tables.items()):
        pk_candidate = guess_primary_key(table_name, df.columns)
        pk_duplicate_rows = None
        pk_is_unique = None
        if pk_candidate:
            pk_duplicate_rows = int(df.duplicated(subset=[pk_candidate]).sum())
            pk_is_unique = pk_duplicate_rows == 0

        rows.append(
            {
                "table": table_name,
                "rows": len(df),
                "columns": len(df.columns),
                "pk_candidate": pk_candidate or "-",
                "pk_is_unique": pk_is_unique,
                "pk_duplicate_rows": pk_duplicate_rows,
                "null_cells": int(df.isna().sum().sum()),
                "null_pct": round(float(df.isna().sum().sum()) / max(df.size, 1) * 100, 2),
                "date_ranges": format_date_ranges(df),
                "column_names": ", ".join(map(str, df.columns)),
            }
        )

    return pd.DataFrame(rows)


def infer_relationship(left_df: pd.DataFrame, left_key: str, right_df: pd.DataFrame, right_key: str) -> str:
    left_non_null = left_df[left_key].dropna()
    right_non_null = right_df[right_key].dropna()

    left_unique = left_non_null.is_unique
    right_unique = right_non_null.is_unique

    if left_unique and right_unique:
        base = "1:1"
    elif left_unique and not right_unique:
        base = "1:N"
    elif not left_unique and right_unique:
        base = "N:1"
    else:
        base = "N:N"

    unmatched_count = int((~left_non_null.isin(set(right_non_null.unique()))).sum())
    if unmatched_count > 0:
        return f"{base} with orphan rows"
    return base


def profile_foreign_key(
    tables: dict[str, pd.DataFrame],
    left_table: str,
    left_key: str,
    right_table: str,
    right_key: str,
) -> dict[str, object]:
    left_df = tables.get(left_table)
    right_df = tables.get(right_table)

    base_row = {
        "left_table": left_table,
        "left_key": left_key,
        "right_table": right_table,
        "right_key": right_key,
        "checked_rows": None,
        "non_null_left_rows": None,
        "unmatched_rows": None,
        "match_rate_pct": None,
        "relationship": "not_checked",
        "note": "Missing table or column.",
    }

    if left_df is None or right_df is None:
        return base_row
    if left_key not in left_df.columns or right_key not in right_df.columns:
        return base_row

    left_non_null = left_df[left_key].dropna()
    right_values = set(right_df[right_key].dropna().unique())
    unmatched_rows = int((~left_non_null.isin(right_values)).sum())
    match_rate_pct = round((1 - unmatched_rows / len(left_non_null)) * 100, 2) if len(left_non_null) else None

    return {
        "left_table": left_table,
        "left_key": left_key,
        "right_table": right_table,
        "right_key": right_key,
        "checked_rows": len(left_df),
        "non_null_left_rows": len(left_non_null),
        "unmatched_rows": unmatched_rows,
        "match_rate_pct": match_rate_pct,
        "relationship": infer_relationship(left_df, left_key, right_df, right_key),
        "note": "All non-null keys matched." if unmatched_rows == 0 else f"Found {unmatched_rows:,} orphan rows.",
    }


def build_foreign_key_profile(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    rows = [
        profile_foreign_key(
            tables,
            relation["source_table"],
            relation["join_key"],
            relation["related_table"],
            relation["join_key"],
        )
        for relation in JOIN_MAP_ROWS
        if relation["related_table"] not in {"customers", "web_traffic"}
    ]
    rows.extend(
        [
            profile_foreign_key(tables, "orders", "customer_id", "customers", "customer_id"),
            profile_foreign_key(tables, "customers", "zip", "geography", "zip"),
            profile_foreign_key(tables, "sales", "Date", "web_traffic", "date"),
        ]
    )
    return pd.DataFrame(rows)


def build_join_map_df() -> pd.DataFrame:
    return pd.DataFrame(JOIN_MAP_ROWS)


def build_table_usage_df() -> pd.DataFrame:
    return pd.DataFrame(TABLE_USAGE_ROWS)


def export_data_understanding_artifacts(project_root: str | Path) -> dict[str, Path]:
    project_path = Path(project_root)
    output_dir = project_path / "artifacts" / "data_understanding"
    output_dir.mkdir(parents=True, exist_ok=True)

    tables = load_tables(project_path / "dataset")
    dataset_summary = build_dataset_summary(tables)
    foreign_key_profile = build_foreign_key_profile(tables)
    join_map = build_join_map_df()
    table_usage = build_table_usage_df()

    dataset_summary_path = output_dir / "dataset_summary.csv"
    foreign_key_profile_path = output_dir / "foreign_key_profile.csv"
    join_map_path = output_dir / "join_map.csv"
    table_usage_path = output_dir / "table_usage.csv"

    dataset_summary.to_csv(dataset_summary_path, index=False)
    foreign_key_profile.to_csv(foreign_key_profile_path, index=False)
    join_map.to_csv(join_map_path, index=False)
    table_usage.to_csv(table_usage_path, index=False)

    return {
        "dataset_summary": dataset_summary_path,
        "foreign_key_profile": foreign_key_profile_path,
        "join_map": join_map_path,
        "table_usage": table_usage_path,
    }


def get_project_root(project_root: str | Path | None = None) -> Path:
    if project_root is not None:
        return Path(project_root)
    return Path(__file__).resolve().parents[1]


def _empty_series(index: pd.Index, default: Any = np.nan, dtype: str = "float64") -> pd.Series:
    return pd.Series(default, index=index, dtype=dtype)


def _get_series(df: pd.DataFrame, column: str, default: Any = np.nan, dtype: str = "float64") -> pd.Series:
    if column in df.columns:
        return df[column]
    return _empty_series(df.index, default=default, dtype=dtype)


def _safe_divide(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    return numerator / denominator.replace(0, np.nan)


def _standardize_sales_dates(sales: pd.DataFrame) -> pd.DataFrame:
    standardized = sales.copy()
    if "Date" in standardized.columns:
        standardized["Date"] = pd.to_datetime(standardized["Date"])
    return standardized.sort_values("Date").drop_duplicates(subset=["Date"])


def _continuous_daily_frame(df: pd.DataFrame, date_col: str) -> pd.DataFrame:
    daily = df.copy()
    daily[date_col] = pd.to_datetime(daily[date_col])
    full_range = pd.date_range(daily[date_col].min(), daily[date_col].max(), freq="D")
    return daily.set_index(date_col).reindex(full_range).rename_axis(date_col).reset_index()


def ensure_stage_directories(project_root: str | Path) -> dict[str, Path]:
    root = get_project_root(project_root)
    directories = {
        "artifacts": root / "artifacts",
        "data_understanding": root / "artifacts" / "data_understanding",
        "mcq": root / "artifacts" / "mcq",
        "eda_planning": root / "artifacts" / "eda_planning",
        "eda": root / "artifacts" / "eda",
        "forecast_baseline": root / "artifacts" / "forecast_baseline",
        "modeling": root / "artifacts" / "modeling",
        "charts": root / "charts",
        "aggregated_tables": root / "aggregated_tables",
        "models": root / "models",
    }
    for path in directories.values():
        path.mkdir(parents=True, exist_ok=True)
    return directories


def build_line_item_facts(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    order_items = tables["order_items"].copy()
    products = tables["products"].copy()
    orders = tables["orders"].copy()
    customers = tables["customers"].copy()
    geography = tables["geography"].copy()

    facts = order_items.merge(products, on="product_id", how="left")

    order_columns = [
        column
        for column in [
            "order_id",
            "order_date",
            "customer_id",
            "zip",
            "order_status",
            "payment_method",
            "device_type",
            "order_source",
        ]
        if column in orders.columns
    ]
    facts = facts.merge(orders[order_columns], on="order_id", how="left")

    customer_columns = [
        column
        for column in [
            "customer_id",
            "zip",
            "city",
            "signup_date",
            "gender",
            "age_group",
            "acquisition_channel",
        ]
        if column in customers.columns
    ]
    customer_lookup = customers[customer_columns].rename(columns={"zip": "customer_zip", "city": "customer_city"})
    facts = facts.merge(customer_lookup, on="customer_id", how="left")

    facts["order_date"] = pd.to_datetime(facts["order_date"])
    facts["geo_zip"] = _get_series(facts, "customer_zip", default=np.nan, dtype="object").combine_first(
        _get_series(facts, "zip", default=np.nan, dtype="object")
    )

    geography_lookup = geography.rename(columns={"zip": "geo_zip"})
    geo_columns = [column for column in ["geo_zip", "region", "district", "city"] if column in geography_lookup.columns]
    facts = facts.merge(geography_lookup[geo_columns], on="geo_zip", how="left", suffixes=("", "_geo"))

    facts["quantity"] = _get_series(facts, "quantity", default=0.0).fillna(0.0)
    facts["unit_price"] = _get_series(facts, "unit_price", default=np.nan).fillna(_get_series(facts, "price", default=0.0))
    facts["discount_amount"] = _get_series(facts, "discount_amount", default=0.0).fillna(0.0)
    facts["cogs"] = _get_series(facts, "cogs", default=0.0).fillna(0.0)
    facts["line_revenue"] = facts["quantity"] * facts["unit_price"] - facts["discount_amount"]
    facts["line_cogs"] = facts["quantity"] * facts["cogs"]
    facts["gross_profit"] = facts["line_revenue"] - facts["line_cogs"]
    facts["gross_margin_pct"] = _safe_divide(facts["gross_profit"], facts["line_revenue"])
    facts["used_promo"] = facts[[column for column in ["promo_id", "promo_id_2"] if column in facts.columns]].notna().any(axis=1)

    return facts


def build_returns_facts(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    returns_df = tables["returns"].copy()
    line_item_facts = build_line_item_facts(tables)

    merge_columns = [
        column
        for column in [
            "order_id",
            "product_id",
            "order_date",
            "segment",
            "category",
            "size",
            "line_revenue",
            "unit_price",
            "customer_id",
            "region",
        ]
        if column in line_item_facts.columns
    ]

    returns_facts = returns_df.merge(
        line_item_facts[merge_columns].drop_duplicates(subset=["order_id", "product_id"]),
        on=["order_id", "product_id"],
        how="left",
    )
    returns_facts["return_date"] = pd.to_datetime(returns_facts["return_date"])
    returns_facts["return_quantity"] = _get_series(returns_facts, "return_quantity", default=1.0).fillna(1.0)
    returns_facts["estimated_return_revenue"] = returns_facts["return_quantity"] * _get_series(
        returns_facts,
        "unit_price",
        default=0.0,
    ).fillna(0.0)
    streetwear_mask = returns_facts["segment"].eq("Streetwear")
    if "category" in returns_facts.columns:
        streetwear_mask = streetwear_mask | returns_facts["category"].eq("Streetwear")
    returns_facts["segment_group"] = np.where(streetwear_mask, "Streetwear", "Other")
    return returns_facts


def build_shipments_facts(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    shipments = tables["shipments"].copy()
    shipments["ship_date"] = pd.to_datetime(shipments["ship_date"])
    shipments["delivery_date"] = pd.to_datetime(shipments["delivery_date"])
    shipments["delay_days"] = (shipments["delivery_date"] - shipments["ship_date"]).dt.days
    return shipments


def build_reviews_facts(tables: dict[str, pd.DataFrame]) -> pd.DataFrame:
    reviews = tables["reviews"].copy()
    line_item_facts = build_line_item_facts(tables)
    review_context = line_item_facts[[column for column in ["order_id", "product_id", "category", "segment", "size"] if column in line_item_facts.columns]]
    reviews = reviews.merge(review_context.drop_duplicates(subset=["order_id", "product_id"]), on=["order_id", "product_id"], how="left")
    reviews["review_date"] = pd.to_datetime(reviews["review_date"])
    return reviews


def build_mcq_outputs(project_root: str | Path) -> tuple[pd.DataFrame, dict[str, pd.DataFrame]]:
    root = get_project_root(project_root)
    tables = load_tables(root / "dataset")
    orders = tables["orders"].copy()
    orders["order_date"] = pd.to_datetime(orders["order_date"])
    line_item_facts = build_line_item_facts(tables)
    returns_facts = build_returns_facts(tables)
    payments = tables["payments"].copy()
    web_traffic = tables["web_traffic"].copy()

    diagnostics: dict[str, pd.DataFrame] = {}
    answer_rows: list[dict[str, object]] = []

    inter_order_gap = (
        orders.sort_values(["customer_id", "order_date"]) 
        .groupby("customer_id")["order_date"]
        .diff()
        .dt.days
        .dropna()
    )
    q1_detail = pd.DataFrame(
        {
            "metric": ["median_inter_order_gap_days", "mean_inter_order_gap_days"],
            "value": [inter_order_gap.median(), inter_order_gap.mean()],
        }
    )
    diagnostics["Q1"] = q1_detail
    answer_rows.append({"Question": "Q1", "Prompt": MCQ_PROMPTS["Q1"], "Answer": "TBD", "Value": round(float(inter_order_gap.median()), 4)})

    q2_detail = (
        line_item_facts.groupby("segment", dropna=False)
        .agg(total_revenue=("line_revenue", "sum"), total_cogs=("line_cogs", "sum"))
        .reset_index()
    )
    q2_detail["gross_margin_pct"] = _safe_divide(q2_detail["total_revenue"] - q2_detail["total_cogs"], q2_detail["total_revenue"])
    q2_detail = q2_detail.sort_values("gross_margin_pct", ascending=False)
    diagnostics["Q2"] = q2_detail
    q2_top = q2_detail.iloc[0]
    answer_rows.append({"Question": "Q2", "Prompt": MCQ_PROMPTS["Q2"], "Answer": "TBD", "Value": f"{q2_top['segment']} ({q2_top['gross_margin_pct']:.4f})"})

    q3_detail = (
        returns_facts.loc[returns_facts["segment_group"].eq("Streetwear")]
        .groupby("return_reason", dropna=False)
        .size()
        .rename("return_count")
        .reset_index()
        .sort_values("return_count", ascending=False)
    )
    diagnostics["Q3"] = q3_detail
    q3_top = q3_detail.iloc[0] if not q3_detail.empty else {"return_reason": "N/A", "return_count": np.nan}
    answer_rows.append({"Question": "Q3", "Prompt": MCQ_PROMPTS["Q3"], "Answer": "TBD", "Value": q3_top["return_reason"]})

    q4_detail = web_traffic.groupby("traffic_source", dropna=False)["bounce_rate"].mean().sort_values().rename("avg_bounce_rate").reset_index()
    diagnostics["Q4"] = q4_detail
    q4_top = q4_detail.iloc[0]
    answer_rows.append({"Question": "Q4", "Prompt": MCQ_PROMPTS["Q4"], "Answer": "TBD", "Value": f"{q4_top['traffic_source']} ({q4_top['avg_bounce_rate']:.4f})"})

    promo_cols = [column for column in ["promo_id", "promo_id_2"] if column in line_item_facts.columns]
    promo_rate = line_item_facts[promo_cols].notna().any(axis=1).mean() if promo_cols else 0.0
    q5_detail = pd.DataFrame({"metric": ["share_with_promotion"], "value": [promo_rate]})
    diagnostics["Q5"] = q5_detail
    answer_rows.append({"Question": "Q5", "Prompt": MCQ_PROMPTS["Q5"], "Answer": "TBD", "Value": round(float(promo_rate), 4)})

    customer_orders = orders.groupby("customer_id").size().rename("order_count").reset_index()
    q6_detail = (
        customer_orders.merge(tables["customers"][["customer_id", "age_group"]], on="customer_id", how="left")
        .groupby("age_group", dropna=False)["order_count"]
        .mean()
        .rename("avg_order_count_per_customer")
        .reset_index()
        .sort_values("avg_order_count_per_customer", ascending=False)
    )
    diagnostics["Q6"] = q6_detail
    q6_top = q6_detail.iloc[0]
    answer_rows.append({"Question": "Q6", "Prompt": MCQ_PROMPTS["Q6"], "Answer": "TBD", "Value": f"{q6_top['age_group']} ({q6_top['avg_order_count_per_customer']:.4f})"})

    q7_detail = (
        line_item_facts.groupby("region", dropna=False)["line_revenue"]
        .sum()
        .rename("estimated_revenue")
        .reset_index()
        .sort_values("estimated_revenue", ascending=False)
    )
    diagnostics["Q7"] = q7_detail
    q7_top = q7_detail.iloc[0]
    answer_rows.append({"Question": "Q7", "Prompt": MCQ_PROMPTS["Q7"], "Answer": "TBD", "Value": f"{q7_top['region']} ({q7_top['estimated_revenue']:.2f})"})

    cancelled_orders = orders.loc[orders["order_status"].str.lower().eq("cancelled"), ["order_id"]]
    q8_detail = (
        cancelled_orders.merge(payments, on="order_id", how="left")
        .groupby("payment_method", dropna=False)
        .size()
        .rename("cancelled_order_count")
        .reset_index()
        .sort_values("cancelled_order_count", ascending=False)
    )
    diagnostics["Q8"] = q8_detail
    q8_top = q8_detail.iloc[0]
    answer_rows.append({"Question": "Q8", "Prompt": MCQ_PROMPTS["Q8"], "Answer": "TBD", "Value": q8_top["payment_method"]})

    ordered_by_size = (
        line_item_facts.groupby("size", dropna=False)["order_id"]
        .nunique()
        .rename("ordered_orders")
        .reset_index()
    )
    returned_by_size = (
        returns_facts.groupby("size", dropna=False)["order_id"]
        .nunique()
        .rename("returned_orders")
        .reset_index()
    )
    q9_detail = ordered_by_size.merge(returned_by_size, on="size", how="left")
    q9_detail["returned_orders"] = q9_detail["returned_orders"].fillna(0)
    q9_detail["return_rate"] = _safe_divide(q9_detail["returned_orders"], q9_detail["ordered_orders"])
    q9_detail = q9_detail.sort_values("return_rate", ascending=False)
    diagnostics["Q9"] = q9_detail
    q9_top = q9_detail.iloc[0]
    answer_rows.append({"Question": "Q9", "Prompt": MCQ_PROMPTS["Q9"], "Answer": "TBD", "Value": f"{q9_top['size']} ({q9_top['return_rate']:.4f})"})

    installment_mask = payments["installments"].fillna(0) > 1
    q10_detail = (
        payments.loc[installment_mask]
        .groupby("installments", dropna=False)["payment_value"]
        .mean()
        .rename("avg_payment_value")
        .reset_index()
        .sort_values("avg_payment_value", ascending=False)
    )
    diagnostics["Q10"] = q10_detail
    q10_top = q10_detail.iloc[0]
    answer_rows.append({"Question": "Q10", "Prompt": MCQ_PROMPTS["Q10"], "Answer": "TBD", "Value": f"{int(q10_top['installments'])} installments ({q10_top['avg_payment_value']:.2f})"})

    final_answers = pd.DataFrame(answer_rows)
    return final_answers, diagnostics


def export_mcq_artifacts(project_root: str | Path) -> dict[str, Path]:
    directories = ensure_stage_directories(project_root)
    final_answers, diagnostics = build_mcq_outputs(project_root)

    final_answers_path = directories["mcq"] / "final_answers_mcq.csv"
    final_answers.to_csv(final_answers_path, index=False)

    output_paths = {"final_answers_mcq": final_answers_path}
    for question, dataframe in diagnostics.items():
        question_path = directories["mcq"] / f"{question.lower()}_diagnostics.csv"
        dataframe.to_csv(question_path, index=False)
        output_paths[question.lower()] = question_path
    return output_paths


def build_eda_plan_tables() -> dict[str, pd.DataFrame]:
    return {
        "theme_plan": pd.DataFrame(EDA_THEME_PLAN_ROWS),
        "chart_plan": pd.DataFrame(EDA_CHART_PLAN_ROWS),
        "join_preparation": pd.DataFrame(EDA_JOIN_PREP_ROWS),
        "insight_taxonomy": pd.DataFrame(INSIGHT_TAXONOMY_ROWS),
    }


def export_eda_plan_artifacts(project_root: str | Path) -> dict[str, Path]:
    directories = ensure_stage_directories(project_root)
    tables = build_eda_plan_tables()
    output_paths: dict[str, Path] = {}
    for name, dataframe in tables.items():
        path = directories["eda_planning"] / f"{name}.csv"
        dataframe.to_csv(path, index=False)
        output_paths[name] = path
    return output_paths


def build_theme_1_aggregates(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    sales = _standardize_sales_dates(tables["sales"])
    line_item_facts = build_line_item_facts(tables)
    returns_facts = build_returns_facts(tables)

    monthly_revenue = (
        sales.assign(year=sales["Date"].dt.year, month=sales["Date"].dt.month)
        .groupby(["year", "month"], as_index=False)
        .agg(Revenue=("Revenue", "sum"), COGS=("COGS", "sum"))
    )
    monthly_revenue["gross_margin"] = monthly_revenue["Revenue"] - monthly_revenue["COGS"]

    revenue_seasonality = monthly_revenue.copy()
    category_quarterly_revenue = (
        line_item_facts.assign(quarter=line_item_facts["order_date"].dt.to_period("Q").astype(str))
        .groupby(["quarter", "category"], as_index=False)["line_revenue"]
        .sum()
        .sort_values(["quarter", "line_revenue"], ascending=[True, False])
    )

    segment_revenue = line_item_facts.groupby("segment", as_index=False)["line_revenue"].sum()
    segment_returns = returns_facts.groupby("segment", as_index=False)["refund_amount"].sum()
    segment_net_revenue = segment_revenue.merge(segment_returns, on="segment", how="left")
    segment_net_revenue["refund_amount"] = segment_net_revenue["refund_amount"].fillna(0.0)
    segment_net_revenue["net_revenue"] = segment_net_revenue["line_revenue"] - segment_net_revenue["refund_amount"]
    segment_net_revenue = segment_net_revenue.sort_values("net_revenue", ascending=False)

    return {
        "theme1_monthly_revenue": monthly_revenue,
        "theme1_revenue_seasonality": revenue_seasonality,
        "theme1_category_quarterly_revenue": category_quarterly_revenue,
        "theme1_segment_net_revenue": segment_net_revenue,
    }


def build_theme_2_aggregates(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    web_traffic = tables["web_traffic"].copy()
    orders = tables["orders"].copy()
    line_item_facts = build_line_item_facts(tables)

    bounce_by_source = (
        web_traffic.groupby("traffic_source", as_index=False)
        .agg(avg_bounce_rate=("bounce_rate", "mean"), sessions=("sessions", "sum"), unique_visitors=("unique_visitors", "sum"))
        .sort_values("avg_bounce_rate")
    )

    source_orders = orders.groupby("order_source", as_index=False).agg(order_count=("order_id", "nunique"))
    source_revenue = line_item_facts.groupby("order_source", as_index=False).agg(revenue=("line_revenue", "sum"))
    source_sessions_orders = bounce_by_source.merge(source_orders, left_on="traffic_source", right_on="order_source", how="left")
    source_sessions_orders = source_sessions_orders.merge(source_revenue, on="order_source", how="left")
    source_sessions_orders["session_to_order_rate"] = _safe_divide(source_sessions_orders["order_count"], source_sessions_orders["sessions"])

    device_mix = orders.groupby("device_type", as_index=False).agg(order_count=("order_id", "nunique")).sort_values("order_count", ascending=False)
    region_revenue = line_item_facts.groupby("region", as_index=False).agg(revenue=("line_revenue", "sum")).sort_values("revenue", ascending=False)

    return {
        "theme2_bounce_by_source": bounce_by_source,
        "theme2_source_sessions_orders": source_sessions_orders,
        "theme2_device_mix": device_mix,
        "theme2_region_revenue": region_revenue,
    }


def build_theme_3_aggregates(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    line_item_facts = build_line_item_facts(tables)
    returns_facts = build_returns_facts(tables)
    shipments = build_shipments_facts(tables)
    reviews = build_reviews_facts(tables)

    ordered_size_category = (
        line_item_facts.groupby(["size", "category"], as_index=False)
        .agg(ordered_orders=("order_id", "nunique"), ordered_quantity=("quantity", "sum"))
    )
    returned_size_category = (
        returns_facts.groupby(["size", "category"], as_index=False)
        .agg(returned_orders=("order_id", "nunique"), returned_quantity=("return_quantity", "sum"))
    )
    return_rate_heatmap = ordered_size_category.merge(returned_size_category, on=["size", "category"], how="left")
    return_rate_heatmap[["returned_orders", "returned_quantity"]] = return_rate_heatmap[["returned_orders", "returned_quantity"]].fillna(0.0)
    return_rate_heatmap["return_rate"] = _safe_divide(return_rate_heatmap["returned_orders"], return_rate_heatmap["ordered_orders"])

    return_reasons = (
        returns_facts.groupby(["segment_group", "return_reason"], as_index=False)
        .agg(return_count=("return_id", "count"), refund_amount=("refund_amount", "sum"))
        .sort_values(["segment_group", "return_count"], ascending=[True, False])
    )

    delay_vs_rating = shipments.merge(
        reviews.groupby("order_id", as_index=False).agg(avg_rating=("rating", "mean")),
        on="order_id",
        how="inner",
    )[["order_id", "delay_days", "avg_rating"]]

    rating_by_category = (
        reviews.groupby("category", as_index=False)
        .agg(avg_rating=("rating", "mean"), review_count=("review_id", "count"))
        .sort_values("avg_rating", ascending=False)
    )

    return {
        "theme3_return_rate_by_size_category": return_rate_heatmap,
        "theme3_return_reasons": return_reasons,
        "theme3_delay_vs_rating": delay_vs_rating,
        "theme3_rating_by_category": rating_by_category,
    }


def build_theme_4_aggregates(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    inventory = tables["inventory"].copy()
    line_item_facts = build_line_item_facts(tables)

    inventory["snapshot_date"] = pd.to_datetime(inventory["snapshot_date"])
    inventory["month_key"] = inventory["snapshot_date"].dt.to_period("M").astype(str)

    stockout_days = inventory.groupby("category", as_index=False).agg(stockout_days=("stockout_days", "sum")).sort_values("stockout_days", ascending=False)
    fill_rate = inventory.groupby(["category", "month_key"], as_index=False).agg(fill_rate=("fill_rate", "mean"))
    sell_through = inventory.groupby("category", as_index=False).agg(sell_through_rate=("sell_through_rate", "mean")).sort_values("sell_through_rate", ascending=False)

    category_revenue = line_item_facts.groupby("category", as_index=False).agg(total_revenue=("line_revenue", "sum"), active_days=("order_date", "nunique"))
    lost_revenue = category_revenue.merge(stockout_days, on="category", how="left")
    lost_revenue["stockout_days"] = lost_revenue["stockout_days"].fillna(0.0)
    lost_revenue["avg_revenue_per_active_day"] = _safe_divide(lost_revenue["total_revenue"], lost_revenue["active_days"])
    lost_revenue["estimated_lost_revenue"] = lost_revenue["avg_revenue_per_active_day"] * lost_revenue["stockout_days"]
    lost_revenue = lost_revenue.sort_values("estimated_lost_revenue", ascending=False)

    return {
        "theme4_stockout_days": stockout_days,
        "theme4_fill_rate": fill_rate,
        "theme4_sell_through": sell_through,
        "theme4_lost_revenue": lost_revenue,
    }


def build_eda_aggregate_tables(project_root: str | Path) -> dict[str, pd.DataFrame]:
    root = get_project_root(project_root)
    tables = load_tables(root / "dataset")
    aggregates: dict[str, pd.DataFrame] = {}
    for builder in [build_theme_1_aggregates, build_theme_2_aggregates, build_theme_3_aggregates, build_theme_4_aggregates]:
        aggregates.update(builder(tables))
    return aggregates


def export_eda_aggregates(project_root: str | Path) -> dict[str, Path]:
    directories = ensure_stage_directories(project_root)
    aggregate_tables = build_eda_aggregate_tables(project_root)
    output_paths: dict[str, Path] = {}
    for name, dataframe in aggregate_tables.items():
        artifact_path = directories["eda"] / f"{name}.csv"
        table_path = directories["aggregated_tables"] / f"{name}.csv"
        dataframe.to_csv(artifact_path, index=False)
        dataframe.to_csv(table_path, index=False)
        output_paths[name] = artifact_path
    return output_paths


def build_daily_auxiliary_features(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    line_item_facts = build_line_item_facts(tables)
    returns_facts = build_returns_facts(tables)
    reviews = build_reviews_facts(tables)
    shipments = build_shipments_facts(tables)
    inventory = tables["inventory"].copy()
    promotions = tables["promotions"].copy()
    web_traffic = tables["web_traffic"].copy()
    orders = tables["orders"].copy()

    web_daily = (
        web_traffic.assign(date=pd.to_datetime(web_traffic["date"]))
        .groupby("date", as_index=False)
        .agg(
            sessions=("sessions", "sum"),
            unique_visitors=("unique_visitors", "sum"),
            page_views=("page_views", "sum"),
            bounce_rate=("bounce_rate", "mean"),
            avg_session_duration_sec=("avg_session_duration_sec", "mean"),
        )
    )

    orders["order_date"] = pd.to_datetime(orders["order_date"])
    order_daily = orders.groupby("order_date", as_index=False).agg(daily_order_count=("order_id", "nunique"))
    order_daily = order_daily.rename(columns={"order_date": "date"})

    qty_daily = (
        line_item_facts.groupby("order_date", as_index=False)
        .agg(daily_qty_sold=("quantity", "sum"), daily_line_revenue=("line_revenue", "sum"))
        .rename(columns={"order_date": "date"})
    )

    promo_spans = promotions.copy()
    promo_spans["start_date"] = pd.to_datetime(promo_spans["start_date"])
    promo_spans["end_date"] = pd.to_datetime(promo_spans["end_date"])
    promo_spans["date"] = promo_spans.apply(lambda row: pd.date_range(row["start_date"], row["end_date"], freq="D"), axis=1)
    promo_daily = (
        promo_spans.explode("date")
        .groupby("date", as_index=False)
        .agg(daily_active_promos=("promo_id", "nunique"), avg_discount_value=("discount_value", "mean"))
    )

    inventory["snapshot_date"] = pd.to_datetime(inventory["snapshot_date"])
    inventory_monthly = inventory.assign(month_key=inventory["snapshot_date"].dt.to_period("M"))
    inventory_monthly = inventory_monthly.groupby("month_key", as_index=False).agg(
        monthly_fill_rate=("fill_rate", "mean"),
        monthly_stockout_days=("stockout_days", "sum"),
        monthly_sell_through_rate=("sell_through_rate", "mean"),
    )

    returns_daily = returns_facts.groupby("return_date", as_index=False).agg(
        daily_returns=("return_id", "count"), daily_refund_amount=("refund_amount", "sum")
    ).rename(columns={"return_date": "date"})

    reviews_daily = reviews.groupby("review_date", as_index=False).agg(daily_avg_rating=("rating", "mean")).rename(columns={"review_date": "date"})
    shipments_daily = shipments.groupby("ship_date", as_index=False).agg(daily_avg_delay=("delay_days", "mean")).rename(columns={"ship_date": "date"})

    return {
        "web_daily": web_daily,
        "order_daily": order_daily,
        "qty_daily": qty_daily,
        "promo_daily": promo_daily,
        "inventory_monthly": inventory_monthly,
        "returns_daily": returns_daily,
        "reviews_daily": reviews_daily,
        "shipments_daily": shipments_daily,
    }


def add_time_features(df: pd.DataFrame, date_col: str = "date") -> pd.DataFrame:
    featured = df.copy()
    featured[date_col] = pd.to_datetime(featured[date_col])
    featured["dayofweek"] = featured[date_col].dt.dayofweek
    featured["month"] = featured[date_col].dt.month
    featured["quarter"] = featured[date_col].dt.quarter
    featured["year"] = featured[date_col].dt.year
    featured["dayofmonth"] = featured[date_col].dt.day
    featured["weekofyear"] = featured[date_col].dt.isocalendar().week.astype(int)
    featured["is_weekend"] = featured["dayofweek"].isin([5, 6]).astype(int)
    featured["is_month_end"] = featured[date_col].dt.is_month_end.astype(int)
    featured["time_index"] = np.arange(len(featured))
    return featured


def add_lag_and_rolling_features(df: pd.DataFrame, target_columns: Iterable[str]) -> pd.DataFrame:
    featured = df.copy()
    for target_column in target_columns:
        if target_column not in featured.columns:
            continue
        target_prefix = target_column.lower()
        for lag in [1, 7, 14, 28]:
            featured[f"{target_prefix}_lag_{lag}"] = featured[target_column].shift(lag)
        for window in [7, 14, 30]:
            shifted = featured[target_column].shift(1)
            featured[f"{target_prefix}_roll_mean_{window}"] = shifted.rolling(window).mean()
            featured[f"{target_prefix}_roll_std_{window}"] = shifted.rolling(window).std()
    return featured


def build_modeling_dataset(project_root: str | Path) -> pd.DataFrame:
    root = get_project_root(project_root)
    tables = load_tables(root / "dataset")
    sales = _standardize_sales_dates(tables["sales"]).rename(columns={"Date": "date"})
    modeling = _continuous_daily_frame(sales, "date")

    feature_frames = build_daily_auxiliary_features(tables)
    for name, frame in feature_frames.items():
        if name == "inventory_monthly":
            continue
        modeling = modeling.merge(frame, on="date", how="left")

    lagged_external_columns = [
        "sessions",
        "unique_visitors",
        "page_views",
        "bounce_rate",
        "avg_session_duration_sec",
        "daily_order_count",
        "daily_qty_sold",
        "daily_line_revenue",
        "daily_active_promos",
        "avg_discount_value",
        "daily_returns",
        "daily_refund_amount",
        "daily_avg_rating",
        "daily_avg_delay",
    ]
    for column in lagged_external_columns:
        if column in modeling.columns:
            modeling[column] = modeling[column].shift(1)

    inventory_monthly = feature_frames["inventory_monthly"].copy()
    modeling["month_key"] = modeling["date"].dt.to_period("M")
    modeling = modeling.merge(inventory_monthly, on="month_key", how="left")

    modeling = add_time_features(modeling, date_col="date")
    modeling = add_lag_and_rolling_features(modeling, target_columns=["Revenue", "COGS"])
    return modeling.sort_values("date").reset_index(drop=True)


def classify_feature_group(feature_name: str) -> str:
    if feature_name in {"dayofweek", "month", "quarter", "year", "dayofmonth", "weekofyear", "is_weekend", "is_month_end", "time_index"}:
        return "time_based"
    if "_lag_" in feature_name:
        return "lag"
    if "_roll_" in feature_name:
        return "rolling"
    if feature_name.startswith("monthly_"):
        return "monthly_operational"
    if feature_name in {"sessions", "unique_visitors", "page_views", "bounce_rate", "avg_session_duration_sec"}:
        return "web_traffic"
    if feature_name.startswith("daily_") or feature_name == "avg_discount_value":
        return "daily_aggregate"
    return "other"


def build_feature_list(modeling_dataset: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    excluded = {"date", "month_key", "Revenue", "COGS"}
    for column in modeling_dataset.columns:
        if column in excluded:
            continue
        rows.append(
            {
                "feature": column,
                "group": classify_feature_group(column),
                "description": f"Auto-generated feature for {column.replace('_', ' ')}.",
            }
        )
    return pd.DataFrame(rows)


def export_modeling_artifacts(project_root: str | Path) -> dict[str, Path]:
    directories = ensure_stage_directories(project_root)
    modeling_dataset = build_modeling_dataset(project_root)
    feature_list = build_feature_list(modeling_dataset)

    modeling_path = directories["modeling"] / "modeling_dataset.parquet"
    feature_list_path = directories["modeling"] / "feature_list.csv"
    model_artifact_path = directories["models"] / "model_candidate.pkl"

    modeling_dataset.to_parquet(modeling_path, index=False)
    feature_list.to_csv(feature_list_path, index=False)
    model_artifact_path.touch(exist_ok=True)

    return {
        "modeling_dataset": modeling_path,
        "feature_list": feature_list_path,
        "model_candidate": model_artifact_path,
    }


def evaluate_regression_predictions(y_true: pd.Series, y_pred: pd.Series, model_name: str) -> dict[str, object]:
    from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

    aligned = pd.concat([y_true.rename("y_true"), y_pred.rename("y_pred")], axis=1).dropna()
    if aligned.empty:
        return {"Model": model_name, "MAE": np.nan, "RMSE": np.nan, "R2": np.nan, "ScoredRows": 0}

    mae = mean_absolute_error(aligned["y_true"], aligned["y_pred"])
    rmse = float(np.sqrt(mean_squared_error(aligned["y_true"], aligned["y_pred"])))
    r2 = r2_score(aligned["y_true"], aligned["y_pred"])
    return {"Model": model_name, "MAE": mae, "RMSE": rmse, "R2": r2, "ScoredRows": len(aligned)}


def split_time_series(df: pd.DataFrame, date_col: str = "date", valid_start: str | None = None, valid_fraction: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame]:
    ordered = df.sort_values(date_col).reset_index(drop=True)
    if valid_start is not None:
        valid_start_ts = pd.Timestamp(valid_start)
        train = ordered.loc[ordered[date_col] < valid_start_ts].copy()
        valid = ordered.loc[ordered[date_col] >= valid_start_ts].copy()
        return train, valid

    split_idx = int(len(ordered) * (1 - valid_fraction))
    return ordered.iloc[:split_idx].copy(), ordered.iloc[split_idx:].copy()


def run_baseline_models(project_root: str | Path, target_col: str = "Revenue", valid_start: str | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    from sklearn.linear_model import LinearRegression

    modeling = build_modeling_dataset(project_root)[["date", target_col]].dropna().copy()
    modeling = modeling.sort_values("date").reset_index(drop=True)
    modeling["time_index"] = np.arange(len(modeling))
    modeling["month"] = modeling["date"].dt.month
    modeling["dayofweek"] = modeling["date"].dt.dayofweek

    train, valid = split_time_series(modeling, valid_start=valid_start)

    full = modeling.copy()
    full["naive_pred"] = full[target_col].shift(1)
    full["seasonal_naive_pred"] = full[target_col].shift(7)
    full["moving_average_pred"] = full[target_col].shift(1).rolling(7).mean()

    regression = LinearRegression()
    regression.fit(train[["time_index"]].assign(month=train["date"].dt.month, dayofweek=train["date"].dt.dayofweek), train[target_col])
    full["linear_regression_pred"] = regression.predict(full[["time_index", "month", "dayofweek"]])

    validation_frame = full.merge(valid[["date"]], on="date", how="inner")
    score_rows = [
        evaluate_regression_predictions(validation_frame[target_col], validation_frame["naive_pred"], "Naive"),
        evaluate_regression_predictions(validation_frame[target_col], validation_frame["seasonal_naive_pred"], "Seasonal Naive"),
        evaluate_regression_predictions(validation_frame[target_col], validation_frame["moving_average_pred"], "Moving Average (7)"),
        evaluate_regression_predictions(validation_frame[target_col], validation_frame["linear_regression_pred"], "Linear Regression"),
    ]
    scores = pd.DataFrame(score_rows).sort_values("RMSE")
    return scores, validation_frame


def plot_baseline_forecasts(validation_frame: pd.DataFrame, target_col: str, output_path: str | Path) -> Path:
    import matplotlib.pyplot as plt

    path = Path(output_path)
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(validation_frame["date"], validation_frame[target_col], label="Actual", linewidth=2)
    for column, label in [
        ("naive_pred", "Naive"),
        ("seasonal_naive_pred", "Seasonal Naive"),
        ("moving_average_pred", "Moving Average (7)"),
        ("linear_regression_pred", "Linear Regression"),
    ]:
        ax.plot(validation_frame["date"], validation_frame[column], label=label, alpha=0.8)
    ax.set_title(f"Baseline forecast comparison for {target_col}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Date")
    ax.set_ylabel(target_col)
    ax.legend()
    plt.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return path


def export_baseline_artifacts(project_root: str | Path, target_col: str = "Revenue", valid_start: str | None = None) -> dict[str, Path]:
    directories = ensure_stage_directories(project_root)
    scores, validation_frame = run_baseline_models(project_root, target_col=target_col, valid_start=valid_start)
    scores_path = directories["forecast_baseline"] / "baseline_scores.csv"
    predictions_path = directories["forecast_baseline"] / "baseline_predictions.csv"
    plot_path = directories["charts"] / "baseline_forecast.png"

    scores.to_csv(scores_path, index=False)
    validation_frame.to_csv(predictions_path, index=False)
    plot_baseline_forecasts(validation_frame, target_col=target_col, output_path=plot_path)

    return {
        "baseline_scores": scores_path,
        "baseline_predictions": predictions_path,
        "baseline_forecast_plot": plot_path,
    }


def get_model_candidates(random_state: int = 42) -> dict[str, Any]:
    from sklearn.linear_model import Ridge

    candidates: dict[str, Any] = {"Ridge": Ridge(alpha=1.0)}
    try:
        from xgboost import XGBRegressor

        candidates["XGBoost"] = XGBRegressor(
            n_estimators=400,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.9,
            colsample_bytree=0.9,
            objective="reg:squarederror",
            random_state=random_state,
        )
    except Exception:
        pass

    try:
        from lightgbm import LGBMRegressor

        candidates["LightGBM"] = LGBMRegressor(
            n_estimators=400,
            learning_rate=0.05,
            num_leaves=31,
            random_state=random_state,
        )
    except Exception:
        pass

    return candidates


def build_training_frame(modeling_dataset: pd.DataFrame, target_col: str = "Revenue") -> tuple[pd.DataFrame, pd.Series]:
    feature_frame = modeling_dataset.drop(columns=[column for column in ["date", "month_key", "Revenue", "COGS"] if column in modeling_dataset.columns])
    aligned = pd.concat([feature_frame, modeling_dataset[target_col]], axis=1).dropna().reset_index(drop=True)
    X = aligned.drop(columns=[target_col])
    y = aligned[target_col]
    return X, y


def evaluate_model_candidates(modeling_dataset: pd.DataFrame, target_col: str = "Revenue", n_splits: int = 5) -> pd.DataFrame:
    from sklearn.base import clone
    from sklearn.model_selection import TimeSeriesSplit

    X, y = build_training_frame(modeling_dataset, target_col=target_col)
    splitter = TimeSeriesSplit(n_splits=n_splits)
    rows: list[dict[str, object]] = []

    for model_name, model in get_model_candidates().items():
        fold_scores = []
        for train_idx, val_idx in splitter.split(X):
            fitted_model = clone(model)
            fitted_model.fit(X.iloc[train_idx], y.iloc[train_idx])
            predictions = pd.Series(fitted_model.predict(X.iloc[val_idx]), index=y.iloc[val_idx].index)
            fold_scores.append(evaluate_regression_predictions(y.iloc[val_idx], predictions, model_name))

        fold_frame = pd.DataFrame(fold_scores)
        rows.append(
            {
                "Model": model_name,
                "MAE": fold_frame["MAE"].mean(),
                "RMSE": fold_frame["RMSE"].mean(),
                "R2": fold_frame["R2"].mean(),
                "Folds": len(fold_frame),
            }
        )

    return pd.DataFrame(rows).sort_values("RMSE")


def export_model_comparison_artifacts(project_root: str | Path, target_col: str = "Revenue") -> dict[str, Path]:
    directories = ensure_stage_directories(project_root)
    modeling_dataset = build_modeling_dataset(project_root)
    model_scores = evaluate_model_candidates(modeling_dataset, target_col=target_col)
    output_path = directories["modeling"] / "model_vs_baseline.csv"
    model_scores.to_csv(output_path, index=False)
    return {"model_vs_baseline": output_path}


def prepare_submission_template(project_root: str | Path) -> pd.DataFrame:
    root = get_project_root(project_root)
    submission = pd.read_csv(root / "dataset" / "sample_submission.csv")
    submission["Date"] = pd.to_datetime(submission["Date"])
    return submission


def run_cli(command: str, project_root: str | Path) -> dict[str, Path]:
    if command == "data-understanding":
        return export_data_understanding_artifacts(project_root)
    if command == "mcq":
        return export_mcq_artifacts(project_root)
    if command == "eda-plan":
        return export_eda_plan_artifacts(project_root)
    if command == "eda":
        return export_eda_aggregates(project_root)
    if command == "baseline":
        return export_baseline_artifacts(project_root)
    if command == "features":
        return export_modeling_artifacts(project_root)
    if command == "model-compare":
        return export_model_comparison_artifacts(project_root)
    raise ValueError(f"Unsupported command: {command}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Competition workflow utilities for the NEU_BRT Datathon repository.")
    parser.add_argument(
        "command",
        choices=["data-understanding", "mcq", "eda-plan", "eda", "baseline", "features", "model-compare"],
        help="Workflow stage to materialize into artifact files.",
    )
    parser.add_argument("--project-root", default=str(get_project_root()), help="Repository root that contains dataset/ and artifact folders.")
    args = parser.parse_args(argv)

    outputs = run_cli(args.command, args.project_root)
    for name, path in outputs.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())