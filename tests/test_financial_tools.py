"""
FinMatrix Copilot — Unit Tests for Financial Analytics Engine
Tests deterministic calculations for SME health metrics and invoice risk scores.
"""

import pytest
from src.financial_tools import (
    calculate_sme_financial_health,
    calculate_invoice_late_risk_score
)


def test_calculate_sme_financial_health_positive():
    """Test health calculation for profitable cash flow."""
    result = calculate_sme_financial_health(inflow=200000, outflow=150000, cash_reserve=300000)
    assert result["net_cash_flow"] == 50000
    assert result["operating_margin_pct"] == 25.0
    assert result["health_status"] == "Healthy"
    assert result["estimated_runway_months"] == 999.0


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