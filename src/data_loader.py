"""Load va parse cac file CSV theo schema de bai."""
import pandas as pd
from pathlib import Path
from src.utils import load_config, get_logger

log = get_logger("data_loader")


def _path(cfg: dict, filename: str) -> str:
    return str(Path(cfg["paths"]["dataset"]) / filename)


def load_sales(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "sales.csv"), parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def load_sample_submission(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "sample_submission.csv"), parse_dates=["Date"])
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def load_products(cfg: dict) -> pd.DataFrame:
    return pd.read_csv(_path(cfg, "products.csv"))


def load_customers(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "customers.csv"), parse_dates=["signup_date"])
    return df


def load_geography(cfg: dict) -> pd.DataFrame:
    return pd.read_csv(_path(cfg, "geography.csv"))


def load_promotions(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "promotions.csv"),
                     parse_dates=["start_date", "end_date"])
    return df


def load_orders(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "orders.csv"), parse_dates=["order_date"])
    return df


def load_order_items(cfg: dict) -> pd.DataFrame:
    return pd.read_csv(_path(cfg, "order_items.csv"))


def load_payments(cfg: dict) -> pd.DataFrame:
    return pd.read_csv(_path(cfg, "payments.csv"))


def load_shipments(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "shipments.csv"),
                     parse_dates=["ship_date", "delivery_date"])
    return df


def load_returns(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "returns.csv"), parse_dates=["return_date"])
    return df


def load_reviews(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "reviews.csv"), parse_dates=["review_date"])
    return df


def load_inventory(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "inventory.csv"), parse_dates=["snapshot_date"])
    return df


def load_web_traffic(cfg: dict) -> pd.DataFrame:
    df = pd.read_csv(_path(cfg, "web_traffic.csv"), parse_dates=["date"])
    return df


def load_all(cfg: dict) -> dict:
    """Tra ve dict chua tat ca cac bang du lieu."""
    log.info("Loading all datasets...")
    tables = {
        "sales":       load_sales(cfg),
        "submission":  load_sample_submission(cfg),
        "products":    load_products(cfg),
        "customers":   load_customers(cfg),
        "geography":   load_geography(cfg),
        "promotions":  load_promotions(cfg),
        "orders":      load_orders(cfg),
        "order_items": load_order_items(cfg),
        "payments":    load_payments(cfg),
        "shipments":   load_shipments(cfg),
        "returns":     load_returns(cfg),
        "reviews":     load_reviews(cfg),
        "inventory":   load_inventory(cfg),
        "web_traffic": load_web_traffic(cfg),
    }
    for name, df in tables.items():
        log.info(f"  {name}: {len(df):,} rows x {df.shape[1]} cols")
    return tables
