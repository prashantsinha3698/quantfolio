"""
Trade generation, minimum trade filtering, and transaction cost estimation.
"""
from typing import Dict, List, Tuple
from app.rebalance.drift import calculate_allocation_drift


def generate_trades(
    current_values: Dict[str, float],
    target_weights: Dict[str, float],
    current_prices: Dict[str, float],
    drift_threshold: float = 0.05,
    minimum_trade_value: float = 1000.0,
    transaction_cost_rate: float = 0.0010,
) -> Tuple[List[Dict[str, any]], Dict[str, any]]:
    """
    Computes actionable BUY/SELL/HOLD trade recommendations:
    Target Value = Total Portfolio Value * Target Weight
    Trade Value = Target Value - Current Value
    """
    total_portfolio_value = sum(current_values.values())
    if total_portfolio_value <= 0:
        total_portfolio_value = 1_000_000.0

    current_weights = {
        ticker: val / total_portfolio_value
        for ticker, val in current_values.items()
    }

    drift_items = calculate_allocation_drift(
        current_weights=current_weights,
        target_weights=target_weights,
        drift_threshold=drift_threshold,
    )

    trade_items = []
    total_buy = 0.0
    total_sell = 0.0
    outside_threshold_count = 0

    for idx, d in enumerate(drift_items):
        ticker = d["ticker"]
        curr_w = d["current_weight"]
        targ_w = d["target_weight"]
        drift = d["drift"]
        status = d["drift_status"]

        curr_val = current_values.get(ticker, 0.0)
        targ_val = total_portfolio_value * targ_w
        trade_val = targ_val - curr_val  # Positive means under target -> BUY

        price = current_prices.get(ticker, 100.0)
        if price <= 0:
            price = 100.0

        if status == "action_required":
            outside_threshold_count += 1

        # Check minimum trade value filter
        if abs(trade_val) < minimum_trade_value:
            action = "HOLD"
            reason = f"Trade delta (${abs(trade_val):,.0f}) is below minimum trade threshold (${minimum_trade_value:,.0f})"
            shares = 0
        elif trade_val > 0:
            action = "BUY"
            shares = int(trade_val // price)
            total_buy += trade_val
            pct_drift = drift * 100
            reason = f"{ticker} is {abs(pct_drift):.1f}% below target allocation"
        else:
            action = "SELL"
            shares = int(abs(trade_val) // price)
            total_sell += abs(trade_val)
            pct_drift = drift * 100
            reason = f"{ticker} is {abs(pct_drift):.1f}% above target allocation"

        trade_items.append({
            "ticker": ticker,
            "current_weight": curr_w,
            "target_weight": targ_w,
            "drift": drift,
            "drift_status": status,
            "current_value": float(round(curr_val, 2)),
            "target_value": float(round(targ_val, 2)),
            "trade_value": float(round(trade_val, 2)),
            "action": action,
            "priority": idx + 1,
            "current_price": float(round(price, 2)),
            "estimated_shares": shares,
            "reason": reason,
        })

    total_turnover = (total_buy + total_sell) / 2.0
    est_cost = (total_buy + total_sell) * transaction_cost_rate

    summary = {
        "rebalance_required": outside_threshold_count > 0,
        "drift_threshold": drift_threshold,
        "assets_outside_threshold": outside_threshold_count,
        "total_buy_value": float(round(total_buy, 2)),
        "total_sell_value": float(round(total_sell, 2)),
        "total_turnover_value": float(round(total_turnover, 2)),
        "estimated_transaction_cost": float(round(est_cost, 2)),
        "transaction_cost_rate": transaction_cost_rate,
    }

    return trade_items, summary
