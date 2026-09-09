"""
Integration tests for FastAPI REST endpoints using TestClient.
"""
from fastapi.testclient import TestClient
import pytest

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_get_portfolio_presets():
    response = client.get("/api/portfolios/presets")
    assert response.status_code == 200
    presets = response.json()
    assert "balanced_growth" in presets
    assert len(presets["balanced_growth"]["holdings"]) == 5


def test_evaluate_portfolio_endpoint():
    payload = {
        "name": "Test Balanced",
        "initial_capital": 100000.0,
        "base_currency": "USD",
        "benchmark": "SPY",
        "holdings": [
            {"ticker": "SPY", "quantity": 100, "target_weight": 0.60, "min_weight": 0.0, "max_weight": 1.0},
            {"ticker": "TLT", "quantity": 400, "target_weight": 0.40, "min_weight": 0.0, "max_weight": 1.0},
        ],
        "date_range": "1Y",
    }
    response = client.post("/api/portfolios/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["current_value"] > 0
    assert len(data["holdings"]) == 2


def test_performance_analytics_endpoint():
    payload = {
        "name": "Test Balanced",
        "initial_capital": 1000000.0,
        "base_currency": "USD",
        "benchmark": "SPY",
        "holdings": [
            {"ticker": "SPY", "quantity": 1000, "target_weight": 0.60, "min_weight": 0.0, "max_weight": 1.0},
            {"ticker": "TLT", "quantity": 4000, "target_weight": 0.40, "min_weight": 0.0, "max_weight": 1.0},
        ],
        "date_range": "6M",
    }
    response = client.post("/api/analytics/performance", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "sharpe_ratio" in data["kpis"]
    assert len(data["time_series"]) > 10


def test_risk_analytics_endpoint():
    payload = {
        "name": "Test Balanced",
        "initial_capital": 1000000.0,
        "base_currency": "USD",
        "benchmark": "SPY",
        "holdings": [
            {"ticker": "SPY", "quantity": 1000, "target_weight": 0.60, "min_weight": 0.0, "max_weight": 1.0},
            {"ticker": "TLT", "quantity": 4000, "target_weight": 0.40, "min_weight": 0.0, "max_weight": 1.0},
        ],
        "date_range": "6M",
    }
    response = client.post("/api/risk/analytics", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "historical_var_95" in data["kpis"]
    assert "risk_contributions" in data
    assert len(data["risk_contributions"]) == 2


def test_optimization_endpoint():
    payload = {
        "name": "Test Balanced",
        "initial_capital": 1000000.0,
        "base_currency": "USD",
        "benchmark": "SPY",
        "holdings": [
            {"ticker": "SPY", "quantity": 1000, "target_weight": 0.50, "min_weight": 0.0, "max_weight": 1.0},
            {"ticker": "QQQ", "quantity": 500, "target_weight": 0.30, "min_weight": 0.0, "max_weight": 1.0},
            {"ticker": "TLT", "quantity": 2000, "target_weight": 0.20, "min_weight": 0.0, "max_weight": 1.0},
        ],
        "date_range": "6M",
    }
    response = client.post("/api/optimization/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "min_volatility" in data
    assert "max_sharpe" in data
    assert len(data["frontier"]) > 5


def test_rebalance_endpoint():
    payload = {
        "name": "Test Balanced",
        "initial_capital": 1000000.0,
        "base_currency": "USD",
        "benchmark": "SPY",
        "holdings": [
            {"ticker": "SPY", "quantity": 1500, "target_weight": 0.50, "min_weight": 0.0, "max_weight": 1.0},
            {"ticker": "TLT", "quantity": 1000, "target_weight": 0.50, "min_weight": 0.0, "max_weight": 1.0},
        ],
        "rebalance_config": {
            "drift_threshold": 0.05,
            "minimum_trade_value": 1000.0,
            "transaction_cost_rate": 0.0010,
        },
        "date_range": "6M",
    }
    response = client.post("/api/rebalance/evaluate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "trades" in data
    assert len(data["trades"]) == 2
