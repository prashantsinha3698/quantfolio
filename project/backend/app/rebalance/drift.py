"""
Allocation drift detection and classification engine.
"""
from typing import Dict, List


def calculate_allocation_drift(
    current_weights: Dict[str, float],
    target_weights: Dict[str, float],
    drift_threshold: float = 0.05,
) -> List[Dict[str, any]]:
    """
    Computes weight drift: Drift_i = w_current,i - w_target,i
    Classifies drift status into:
    - 'normal': |Drift| <= threshold * 0.5
    - 'warning': threshold * 0.5 < |Drift| <= threshold
    - 'action_required': |Drift| > threshold
    """
    all_tickers = sorted(list(set(list(current_weights.keys()) + list(target_weights.keys()))))
    drift_reports = []

    for ticker in all_tickers:
        curr_w = current_weights.get(ticker, 0.0)
        targ_w = target_weights.get(ticker, 0.0)
        drift = curr_w - targ_w
        abs_drift = abs(drift)

        if abs_drift > drift_threshold:
            status = "action_required"
        elif abs_drift > (drift_threshold * 0.5):
            status = "warning"
        else:
            status = "normal"

        drift_reports.append({
            "ticker": ticker,
            "current_weight": float(round(curr_w, 4)),
            "target_weight": float(round(targ_w, 4)),
            "drift": float(round(drift, 4)),
            "abs_drift": float(round(abs_drift, 4)),
            "drift_status": status,
        })

    # Sort by absolute drift descending (largest drift first)
    drift_reports.sort(key=lambda x: x["abs_drift"], reverse=True)
    return drift_reports
