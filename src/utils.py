"""Tien ich chung: seed, logging, IO, config."""
import os
import random
import logging
import yaml
import numpy as np
import pandas as pd
from pathlib import Path


def set_seed(seed: int = 42):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)


def load_config(path: str = "config.yaml") -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_logger(name: str, level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s %(name)s: %(message)s",
                                               datefmt="%H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


def ensure_dirs(cfg: dict):
    for key in ["outputs", "figures", "models", "cv_results", "submissions", "report_figures"]:
        Path(cfg["paths"][key]).mkdir(parents=True, exist_ok=True)


def save_fig(fig, name: str, cfg: dict, dpi: int = 150):
    """Luu figure vao outputs/figures/ va report/figures/."""
    for folder in [cfg["paths"]["figures"], cfg["paths"]["report_figures"]]:
        Path(folder).mkdir(parents=True, exist_ok=True)
        fig.savefig(f"{folder}/{name}.png", dpi=dpi, bbox_inches="tight")
        fig.savefig(f"{folder}/{name}.pdf", bbox_inches="tight")


def save_submission(df: pd.DataFrame, name: str, cfg: dict):
    path = f"{cfg['paths']['submissions']}/{name}.csv"
    df.to_csv(path, index=False)
    print(f"Saved: {path} ({len(df)} rows)")
    return path
