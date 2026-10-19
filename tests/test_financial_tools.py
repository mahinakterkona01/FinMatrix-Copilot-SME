"""
FinMatrix Copilot — Unit Tests for Financial Analytics Engine
Tests deterministic calculations for SME health metrics and invoice risk scores.
"""

import pytest
import pandas as pd
import numpy as np
from src.financial_tools import (
    calculate_sme_financial_health,
    calculate_invoice_late_risk_score
)

from src.financial_tools import (
    calculate_cash_position,
    detect_overdue_invoices,
    calculate_burn_rate,
)


def test_calculate_sme_financial_health_positive():
    """Test health calculation for profitable cash flow."""
    result = calculate_sme_financial_health(inflow=200000, outflow=150000, cash_reserve=300000)
    assert result["net_cash_flow"] == 50000
    assert result["operating_margin_pct"] == 25.0
    assert result["health_status"] == "Healthy"
    assert result["estimated_runway_months"] is None


def test_calculate_sme_financial_health_negative():
    """Test health calculation for negative cash flow (burn rate)."""
    result = calculate_sme_financial_health(inflow=100000, outflow=150000, cash_reserve=100000)
    assert result["net_cash_flow"] == -50000
    assert result["monthly_burn_rate"] == 50000
    assert result["estimated_runway_months"] == 2.0
    assert result["health_status"] == "Liquidity Warning"


def test_calculate_invoice_late_risk_score():
    """Test invoice risk score bounds and severity labeling."""
    low_risk = calculate_invoice_late_risk_score(invoice_amount=10000, payment_terms_days=15)
    assert low_risk["risk_level"] == "Low"

    high_risk = calculate_invoice_late_risk_score(
        invoice_amount=80000, payment_terms_days=45, historical_late_count=2
    )
    assert high_risk["risk_level"] == "High"
    assert high_risk["risk_score"] <= 1.0


def test_calculate_sme_financial_health_zero_burn_has_no_runway():
    """Runway is not applicable when inflow equals outflow."""
    result = calculate_sme_financial_health(
        inflow=100000,
        outflow=100000,
        cash_reserve=50000,
    )
    assert result["net_cash_flow"] == 0
    assert result["monthly_burn_rate"] == 0.0
    assert result["estimated_runway_months"] is None


@pytest.mark.parametrize("period", [0, -1, 1.5, True])
def test_burn_rate_rejects_nonpositive_period(period):
    with pytest.raises(ValueError):
        calculate_burn_rate(pd.DataFrame(columns=["transaction_type", "amount"]), period)


@pytest.mark.parametrize("amount", [-1, float("nan"), float("inf"), "not-a-number"])
def test_cash_position_rejects_invalid_amounts(amount):
    df = pd.DataFrame([{"transaction_type": "inflow", "amount": amount}])
    with pytest.raises(ValueError):
        calculate_cash_position(df)


def test_cash_position_rejects_unknown_transaction_type():
    df = pd.DataFrame([{"transaction_type": "refund-ish", "amount": 10}])
    with pytest.raises(ValueError):
        calculate_cash_position(df)


def test_cash_position_empty_dataframe_without_columns_is_zero():
    result = calculate_cash_position(pd.DataFrame(), initial_balance=125.0)
    assert result["total_inflow"] == 0.0
    assert result["total_outflow"] == 0.0
    assert result["ending_balance"] == 125.0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"inflow": -1, "outflow": 0, "cash_reserve": 0},
        {"inflow": float("nan"), "outflow": 0, "cash_reserve": 0},
        {"inflow": 0, "outflow": float("inf"), "cash_reserve": 0},
        {"inflow": 0, "outflow": 0, "cash_reserve": -1},
    ],
)
def test_financial_health_rejects_invalid_values(kwargs):
    with pytest.raises(ValueError):
        calculate_sme_financial_health(**kwargs)


def test_invoice_due_today_is_not_overdue():
    invoices = pd.DataFrame([{
        "invoice_id": "INV-1", "customer_id": "C-1",
        "amount": 100, "due_date": "2026-10-18", "status": "unpaid",
    }])
    result = detect_overdue_invoices(invoices, "2026-10-18")
    assert result["overdue_count"] == 0
    assert result["total_overdue_amount"] == 0.0


def test_invoice_invalid_due_date_is_rejected():
    invoices = pd.DataFrame([{
        "invoice_id": "INV-1", "customer_id": "C-1",
        "amount": 100, "due_date": "not-a-date", "status": "unpaid",
    }])
    with pytest.raises(ValueError):
        detect_overdue_invoices(invoices, "2026-10-18")


@pytest.mark.parametrize(
    "kwargs",
    [
        {"invoice_amount": -1, "payment_terms_days": 10},
        {"invoice_amount": float("nan"), "payment_terms_days": 10},
        {"invoice_amount": 10, "payment_terms_days": -1},
        {"invoice_amount": 10, "payment_terms_days": 10, "historical_late_count": -1},
    ],
)
def test_invoice_risk_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        calculate_invoice_late_risk_score(**kwargs)
