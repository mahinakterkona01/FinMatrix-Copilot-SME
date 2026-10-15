"""
FinMatrix Copilot— Deterministic Financial Engine
Contains pure, verifiable Python functions for financial calculations,
cash position tracking, overdue invoice detection, burn rate, and ratio calculations.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


def calculate_cash_position(df_transactions: pd.DataFrame, initial_balance: float = 0.0) -> Dict[str, Any]:
    """
    Calculates total inflows, total outflows, and ending cash balance deterministically.
    """
    if df_transactions.empty:
        return {
            "initial_balance": initial_balance,
            "total_inflow": 0.0,
            "total_outflow": 0.0,
            "net_cash_flow": 0.0,
            "ending_balance": initial_balance,
            "transaction_count": 0
        }

    inflows = df_transactions[df_transactions["transaction_type"].str.lower() == "inflow"]["amount"].sum()
    outflows = df_transactions[df_transactions["transaction_type"].str.lower() == "outflow"]["amount"].sum()
    
    net_flow = float(inflows - outflows)
    ending_balance = float(initial_balance + net_flow)

    return {
        "initial_balance": float(initial_balance),
        "total_inflow": float(inflows),
        "total_outflow": float(outflows),
        "net_cash_flow": net_flow,
        "ending_balance": ending_balance,
        "transaction_count": int(len(df_transactions))
    }


def detect_overdue_invoices(df_invoices: pd.DataFrame, current_date_str: str) -> Dict[str, Any]:
    """
    Identifies unpaid invoices past due date and sums total overdue exposure.
    """
    if df_invoices.empty:
        return {"overdue_count": 0, "total_overdue_amount": 0.0, "overdue_invoices": []}

    df_inv = df_invoices.copy()
    df_inv["due_date"] = pd.to_datetime(df_inv["due_date"])
    ref_date = pd.to_datetime(current_date_str)

    overdue_mask = (df_inv["due_date"] < ref_date) & (df_inv["status"].str.lower() != "paid")
    df_overdue = df_inv[overdue_mask]

    return {
        "overdue_count": int(len(df_overdue)),
        "total_overdue_amount": float(df_overdue["amount"].sum()),
        "overdue_invoices": df_overdue[["invoice_id", "customer_id", "amount", "due_date"]].to_dict(orient="records")
    }


def calculate_burn_rate(df_transactions: pd.DataFrame, period_days: int = 30) -> Dict[str, float]:
    """
    Calculates average daily and monthly operating expense burn rate.
    """
    outflows = df_transactions[df_transactions["transaction_type"].str.lower() == "outflow"]["amount"].sum()
    daily_burn = float(outflows / max(period_days, 1))
    monthly_burn = float(daily_burn * 30)

    return {
        "daily_burn_rate": daily_burn,
        "monthly_burn_rate": monthly_burn
    }


def calculate_sme_financial_health(
    inflow: float,
    outflow: float,
    cash_reserve: float
) -> Dict[str, Any]:
    """
    Calculates key SME financial indicators deterministically.
    """
    net_cash_flow = round(inflow - outflow, 2)
    operating_margin = round((net_cash_flow / inflow * 100), 2) if inflow > 0 else 0.0

    monthly_burn_rate = round(outflow - inflow, 2) if outflow > inflow else 0.0
    
    if monthly_burn_rate > 0:
        estimated_runway = round(cash_reserve / monthly_burn_rate, 1)
    else:
        estimated_runway = 999.0  # Net positive cash flow, infinite operational runway

    return {
        "gross_inflow": inflow,
        "gross_outflow": outflow,
        "net_cash_flow": net_cash_flow,
        "operating_margin_pct": operating_margin,
        "monthly_burn_rate": monthly_burn_rate,
        "estimated_runway_months": estimated_runway,
        "health_status": "Healthy" if net_cash_flow >= 0 else "Liquidity Warning"
    }


def calculate_invoice_late_risk_score(
    invoice_amount: float,
    payment_terms_days: int,
    historical_late_count: int = 0
) -> Dict[str, Any]:
    """
    Computes rule-based risk weights for customer invoice defaults.
    """
    base_score = 0.1
    if payment_terms_days > 30:
        base_score += 0.3
    if invoice_amount > 50000:
        base_score += 0.25
    if historical_late_count > 0:
        base_score += 0.35

    final_risk_score = round(min(base_score, 1.0), 2)
    risk_level = "High" if final_risk_score >= 0.6 else ("Medium" if final_risk_score >= 0.3 else "Low")

    return {
        "invoice_amount": invoice_amount,
        "risk_score": final_risk_score,
        "risk_level": risk_level
    }