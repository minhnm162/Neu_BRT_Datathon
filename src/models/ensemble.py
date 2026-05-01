"""
Ensemble: Blend weight optimization toi uu dong thoi MAE, RMSE, R2.
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import List, Dict, Tuple

from src.metrics import composite_score, evaluate, mae, rmse, r2
from src.utils import get_logger

log = get_logger("ensemble")


def blend_predictions(preds_list: List[np.ndarray],
                      weights: np.ndarray) -> np.ndarray:
    """Weighted average cua nhieu model predictions."""
    weights = np.array(weights)
    weights = weights / weights.sum()
    return sum(w * p for w, p in zip(weights, preds_list))


def optimize_weights(preds_list: List[np.ndarray],
                     y_true: np.ndarray,
                     n_models: int = None,
                     w_mae: float = 0.4,
                     w_rmse: float = 0.4,
                     w_r2: float = 0.2,
                     n_restarts: int = 10,
                     seed: int = 42) -> Tuple[np.ndarray, dict]:
    """
    Tim bo trong so toi uu (simplex) minimize composite score.
    Chay nhieu lan voi khoi tao ngau nhien de tranh local minima.
    """
    np.random.seed(seed)
    n = n_models or len(preds_list)

    def objective(w):
        w = np.abs(w)
        w = w / (w.sum() + 1e-12)
        preds = blend_predictions(preds_list, w)
        return composite_score(y_true, preds, w_mae, w_rmse, w_r2)

    constraints = {"type": "eq", "fun": lambda w: np.sum(np.abs(w)) - 1}
    bounds = [(0, 1)] * n

    best_result = None
    best_score  = np.inf

    for _ in range(n_restarts):
        w0 = np.random.dirichlet(np.ones(n))
        res = minimize(objective, w0, method="SLSQP",
                       bounds=bounds, constraints=constraints,
                       options={"ftol": 1e-9, "maxiter": 1000})
        if res.fun < best_score:
            best_score  = res.fun
            best_result = res

    optimal_w = np.abs(best_result.x)
    optimal_w = optimal_w / optimal_w.sum()

    final_preds = blend_predictions(preds_list, optimal_w)
    metrics = evaluate(y_true, final_preds, label="Ensemble (optimal weights)")
    metrics["weights"] = optimal_w.tolist()

    log.info(f"Optimal weights: {[f'{w:.3f}' for w in optimal_w]}")
    return optimal_w, metrics


def optimize_weights_mae(preds_list, y_true, **kwargs):
    """Toi uu chủ yếu MAE (cho Kaggle public leaderboard)."""
    return optimize_weights(preds_list, y_true, w_mae=0.7, w_rmse=0.2, w_r2=0.1, **kwargs)


def optimize_weights_balanced(preds_list, y_true, **kwargs):
    """Toi uu can bang ca 3 metrics."""
    return optimize_weights(preds_list, y_true, w_mae=0.4, w_rmse=0.4, w_r2=0.2, **kwargs)


def optimize_weights_rmse(preds_list, y_true, **kwargs):
    """Toi uu RMSE/R2."""
    return optimize_weights(preds_list, y_true, w_mae=0.1, w_rmse=0.5, w_r2=0.4, **kwargs)


def compare_blend_strategies(preds_list: List[np.ndarray],
                              y_true: np.ndarray,
                              model_names: List[str],
                              seed: int = 42) -> pd.DataFrame:
    """
    So sanh 3 chien luoc blend va tra ve DataFrame ket qua.
    """
    strategies = {
        "Equal Weight":  (np.ones(len(preds_list)) / len(preds_list), {}),
    }

    # Optimize 3 huong
    for strategy_name, opt_fn in [
        ("Blend (MAE-heavy)", optimize_weights_mae),
        ("Blend (Balanced)",  optimize_weights_balanced),
        ("Blend (RMSE-heavy)", optimize_weights_rmse),
    ]:
        w, metrics = opt_fn(preds_list, y_true, seed=seed)
        strategies[strategy_name] = (w, metrics)

    rows = []
    for name, (w, _) in strategies.items():
        preds = blend_predictions(preds_list, w)
        metrics = evaluate(y_true, preds)
        rows.append({
            "Strategy": name,
            "MAE":  metrics["mae"],
            "RMSE": metrics["rmse"],
            "R2":   metrics["r2"],
            "Composite": metrics["composite"],
        })

    # Them tung model don le
    for mname, preds in zip(model_names, preds_list):
        metrics = evaluate(y_true, preds)
        rows.append({
            "Strategy": mname,
            "MAE":  metrics["mae"],
            "RMSE": metrics["rmse"],
            "R2":   metrics["r2"],
            "Composite": metrics["composite"],
        })

    return pd.DataFrame(rows).sort_values("Composite")
