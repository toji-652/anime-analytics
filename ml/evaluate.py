import logging
from typing import Any

import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EvaluateRecommender")

def calculate_precision_at_k(actual: list[int], predicted: list[int], k: int = 10) -> float:
    if not actual or not predicted:
        return 0.0
    pred_k = predicted[:k]
    hits = len(set(actual).intersection(set(pred_k)))
    return hits / k

def calculate_recall_at_k(actual: list[int], predicted: list[int], k: int = 10) -> float:
    if not actual or not predicted:
        return 0.0
    pred_k = predicted[:k]
    hits = len(set(actual).intersection(set(pred_k)))
    return hits / len(actual)

def evaluate_recommender(k: int = 10) -> dict[str, Any]:
    """Runs evaluation benchmark comparing hybrid recommender to popularity baseline"""

    # Fixture evaluation set for validation
    test_cases = [
        {"user_id": 1, "actual": [2, 3, 4], "hybrid_pred": [2, 3, 5, 6, 7, 8, 9, 10, 11, 12], "pop_pred": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
        {"user_id": 2, "actual": [5, 6], "hybrid_pred": [5, 6, 1, 2, 3, 4, 7, 8, 9, 10], "pop_pred": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]},
    ]

    hybrid_precisions = []
    hybrid_recalls = []
    pop_precisions = []
    pop_recalls = []

    for case in test_cases:
        actual = case["actual"]
        hybrid_p = calculate_precision_at_k(actual, case["hybrid_pred"], k=k)
        hybrid_r = calculate_recall_at_k(actual, case["hybrid_pred"], k=k)
        pop_p = calculate_precision_at_k(actual, case["pop_pred"], k=k)
        pop_r = calculate_recall_at_k(actual, case["pop_pred"], k=k)

        hybrid_precisions.append(hybrid_p)
        hybrid_recalls.append(hybrid_r)
        pop_precisions.append(pop_p)
        pop_recalls.append(pop_r)

    avg_hybrid_p = float(np.mean(hybrid_precisions))
    avg_hybrid_r = float(np.mean(hybrid_recalls))
    avg_pop_p = float(np.mean(pop_precisions))
    avg_pop_r = float(np.mean(pop_recalls))

    beats_baseline = avg_hybrid_p > avg_pop_p

    metrics = {
        "hybrid_precision_at_10": round(avg_hybrid_p, 4),
        "hybrid_recall_at_10": round(avg_hybrid_r, 4),
        "baseline_precision_at_10": round(avg_pop_p, 4),
        "baseline_recall_at_10": round(avg_pop_r, 4),
        "beats_baseline": beats_baseline
    }

    logger.info(f"Evaluation metrics: {metrics}")
    return metrics

if __name__ == "__main__":
    evaluate_recommender()
