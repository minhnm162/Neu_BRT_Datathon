"""
Aggregate transactional data (orders, order_items, web_traffic, inventory)
thanh daily features. Tat ca features chỉ dung du lieu <= D-1.
"""
import numpy as np
import pandas as pd


def build_daily_orders(orders: pd.DataFrame,
                       order_items: pd.DataFrame,
                       payments: pd.DataFrame,
                       customers: pd.DataFrame,
                       geography: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate orders + items theo ngay dat hang.
    Tra ve DataFrame index = Date.
    """
    # Join items vao orders
    oi = order_items.merge(orders[["order_id", "order_date", "customer_id",
                                   "order_status", "payment_method",
                                   "device_type", "order_source", "zip"]],
                           on="order_id", how="left")

    # Join payments
    pay = payments[["order_id", "payment_value"]]
    o_pay = orders[["order_id", "order_date", "customer_id",
                    "order_status", "payment_method",
                    "device_type", "order_source", "zip"]].merge(
        pay, on="order_id", how="left"
    )

    # Join customers de lay signup_date
    o_pay = o_pay.merge(customers[["customer_id", "signup_date", "age_group",
                                    "gender", "acquisition_channel"]],
                        on="customer_id", how="left")

    # Join geography de lay region
    o_pay = o_pay.merge(geography[["zip", "region"]], on="zip", how="left")

    # Xac dinh khach hang moi (dang ky cung ngay)
    o_pay["is_new_customer"] = (
        o_pay["order_date"].dt.date == o_pay["signup_date"].dt.date
    ).astype(int)

    # Aggregate theo ngay
    grp = o_pay.groupby("order_date")

    daily = pd.DataFrame(index=grp.groups.keys())
    daily.index.name = "Date"
    daily = daily.reset_index()

    agg = grp.agg(
        n_orders=("order_id", "nunique"),
        n_customers=("customer_id", "nunique"),
        n_new_customers=("is_new_customer", "sum"),
        total_payment=("payment_value", "sum"),
        avg_payment=("payment_value", "mean"),
    ).reset_index()
    agg = agg.rename(columns={"order_date": "Date"})

    # Payment method mix
    pm_dummies = pd.get_dummies(o_pay["payment_method"], prefix="pm")
    pm_day = pd.concat([o_pay[["order_date"]], pm_dummies], axis=1)
    pm_agg = pm_day.groupby("order_date").mean().reset_index()
    pm_agg = pm_agg.rename(columns={"order_date": "Date"})

    # Device type mix
    dev_dummies = pd.get_dummies(o_pay["device_type"], prefix="dev")
    dev_day = pd.concat([o_pay[["order_date"]], dev_dummies], axis=1)
    dev_agg = dev_day.groupby("order_date").mean().reset_index()
    dev_agg = dev_agg.rename(columns={"order_date": "Date"})

    # Order source mix
    src_dummies = pd.get_dummies(o_pay["order_source"], prefix="src")
    src_day = pd.concat([o_pay[["order_date"]], src_dummies], axis=1)
    src_agg = src_day.groupby("order_date").mean().reset_index()
    src_agg = src_agg.rename(columns={"order_date": "Date"})

    # Items aggregate: n_items, discount_ratio
    item_agg = oi.groupby("order_date").agg(
        n_items=("quantity", "sum"),
        total_discount=("discount_amount", "sum"),
        n_order_lines=("order_id", "count"),
        pct_promo=("promo_id", lambda x: x.notna().mean()),
    ).reset_index().rename(columns={"order_date": "Date"})

    # Merge tat ca
    result = agg
    for df in [pm_agg, dev_agg, src_agg, item_agg]:
        result = result.merge(df, on="Date", how="left")

    # Tinh them
    result["new_customer_ratio"] = result["n_new_customers"] / (result["n_customers"] + 1e-6)
    result["items_per_order"]    = result["n_items"] / (result["n_orders"] + 1e-6)
    result["aov"]                = result["total_payment"] / (result["n_orders"] + 1e-6)

    return result.sort_values("Date").reset_index(drop=True)


def build_daily_web_traffic(web_traffic: pd.DataFrame) -> pd.DataFrame:
    """Pivot web_traffic: moi nguon la mot tap features rieng."""
    df = web_traffic.copy()
    df["conversion_proxy"] = (df["sessions"] / (df["unique_visitors"] + 1e-6))

    # Aggregate theo ngay (cong tat ca nguon)
    total = df.groupby("date").agg(
        total_sessions=("sessions", "sum"),
        total_visitors=("unique_visitors", "sum"),
        total_pageviews=("page_views", "sum"),
        avg_bounce_rate=("bounce_rate", "mean"),
        avg_session_duration=("avg_session_duration_sec", "mean"),
    ).reset_index().rename(columns={"date": "Date"})

    # Traffic source mix (% cua tung nguon)
    total_sess = df.groupby("date")["sessions"].transform("sum")
    df["sessions_pct"] = df["sessions"] / (total_sess + 1e-6)
    src_pivot = df.pivot_table(
        index="date", columns="traffic_source",
        values="sessions_pct", aggfunc="mean"
    ).reset_index()
    src_pivot.columns = [f"traffic_pct_{c}" if c != "date" else "Date"
                         for c in src_pivot.columns]

    bounce_pivot = df.pivot_table(
        index="date", columns="traffic_source",
        values="bounce_rate", aggfunc="mean"
    ).reset_index()
    bounce_pivot.columns = [f"bounce_{c}" if c != "date" else "Date"
                             for c in bounce_pivot.columns]

    result = total.merge(src_pivot, on="Date", how="left")
    result = result.merge(bounce_pivot, on="Date", how="left")
    return result.sort_values("Date").reset_index(drop=True)


def build_daily_inventory(inventory: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate inventory theo snapshot_date (cuoi thang).
    Forward-fill sang cac ngay trong thang.
    """
    agg = inventory.groupby("snapshot_date").agg(
        total_stock=("stock_on_hand", "sum"),
        avg_fill_rate=("fill_rate", "mean"),
        avg_days_supply=("days_of_supply", "mean"),
        avg_sell_through=("sell_through_rate", "mean"),
        n_stockout=("stockout_flag", "sum"),
        n_overstock=("overstock_flag", "sum"),
        n_reorder=("reorder_flag", "sum"),
        total_units_sold=("units_sold", "sum"),
        total_units_received=("units_received", "sum"),
    ).reset_index().rename(columns={"snapshot_date": "Date"})
    return agg.sort_values("Date").reset_index(drop=True)


def build_daily_promotions(promotions: pd.DataFrame,
                           date_range: pd.DatetimeIndex) -> pd.DataFrame:
    """
    Xay dung daily promo features: so luong promo dang chay, muc do giam gia.
    """
    rows = []
    for date in date_range:
        active = promotions[
            (promotions["start_date"] <= date) &
            (promotions["end_date"] >= date)
        ]
        rows.append({
            "Date": date,
            "n_active_promos": len(active),
            "max_pct_discount": active[active["promo_type"] == "percentage"]["discount_value"].max()
                                 if len(active) > 0 else 0,
            "max_fixed_discount": active[active["promo_type"] == "fixed"]["discount_value"].max()
                                   if len(active) > 0 else 0,
            "has_stackable_promo": int((active["stackable_flag"] == 1).any()) if len(active) > 0 else 0,
            "n_categories_promo": active["applicable_category"].notna().sum() if len(active) > 0 else 0,
        })
    return pd.DataFrame(rows)


def add_lagged_transactional(df: pd.DataFrame,
                              trans_df: pd.DataFrame,
                              date_col_trans: str = "Date",
                              lag: int = 1) -> pd.DataFrame:
    """
    Join transactional features vao df voi lag so ngay de tranh leakage.
    df phai co cot 'Date'.
    """
    shifted = trans_df.copy()
    shifted[date_col_trans] = shifted[date_col_trans] + pd.Timedelta(days=lag)
    result = df.merge(shifted, left_on="Date", right_on=date_col_trans, how="left")
    if date_col_trans != "Date" and date_col_trans in result.columns:
        result = result.drop(columns=[date_col_trans])
    return result
