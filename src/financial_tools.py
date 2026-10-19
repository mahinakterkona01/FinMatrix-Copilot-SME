"""
FinMatrix Copilot— Deterministic Financial Engine
Contains pure, verifiable Python functions for financial calculations,
cash position tracking, overdue invoice detection, burn rate, and ratio calculations.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np


def _finite_number(value: Any, name: str) -> float:
    """Convert a numeric input to a finite float, rejecting booleans and invalid values."""
    if isinstance(value, (bool, np.bool_)):
        raise ValueError(f"{name} must be a finite number")
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not np.isfinite(number):
        raise ValueError(f"{name} must be a finite number")
    return number


def _validated_transactions(df_transactions: pd.DataFrame) -> pd.DataFrame:
    """Validate transaction schema, types, and nonnegative finite amounts."""
    required = {"transaction_type", "amount"}
    missing = required - set(df_transactions.columns)
    if missing:
        raise ValueError(f"Missing required transaction columns: {', '.join(sorted(missing))}")

    tx = df_transactions.copy()
    if tx["transaction_type"].isna().any():
        raise ValueError("transaction_type cannot be missing")
    tx["transaction_type"] = tx["transaction_type"].astype(str).str.strip().str.lower()
    if not tx["transaction_type"].isin(["inflow", "outflow"]).all():
        raise ValueError("transaction_type must be 'inflow' or 'outflow'")

    try:
        amounts = pd.to_numeric(tx["amount"], errors="raise")
        numeric_amounts = amounts.to_numpy(dtype=float)
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Transaction amounts must be finite numbers") from exc
    if not np.isfinite(numeric_amounts).all():
        raise ValueError("Transaction amounts must be finite numbers")
    if (amounts < 0).any():
        raise ValueError("Transaction amounts cannot be negative")

    tx["amount"] = amounts.astype(float)
    return tx


def calculate_cash_position(df_transactions: pd.DataFrame, initial_balance: float = 0.0) -> Dict[str, Any]:
    """Calculate cash totals from validated transaction records."""
    initial_balance = _finite_number(initial_balance, "initial_balance")
    if not isinstance(df_transactions, pd.DataFrame):
        raise ValueError("df_transactions must be a pandas DataFrame")

    if df_transactions.empty:
        inflows = outflows = 0.0
    else:
        tx = _validated_transactions(df_transactions)
        inflows = float(tx.loc[tx["transaction_type"] == "inflow", "amount"].sum())
        outflows = float(tx.loc[tx["transaction_type"] == "outflow", "amount"].sum())

    net_flow = float(inflows - outflows)
    return {
        "initial_balance": float(initial_balance),
        "total_inflow": float(inflows),
        "total_outflow": float(outflows),
        "net_cash_flow": net_flow,
        "ending_balance": float(initial_balance + net_flow),
        "transaction_count": int(len(df_transactions)),
    }



def detect_overdue_invoices(df_invoices: pd.DataFrame, current_date_str: str) -> Dict[str, Any]:
    """Return unpaid invoices whose calendar due date precedes the reference date."""
    if not isinstance(df_invoices, pd.DataFrame):
        raise ValueError("df_invoices must be a pandas DataFrame")
    if df_invoices.empty:
        return {"overdue_count": 0, "total_overdue_amount": 0.0, "overdue_invoices": []}

    required = {"invoice_id", "customer_id", "amount", "due_date", "status"}
    missing = required - set(df_invoices.columns)
    if missing:
        raise ValueError(f"Missing required invoice columns: {', '.join(sorted(missing))}")

    try:
        ref_date = pd.to_datetime(current_date_str, errors="raise")
        due_dates = pd.to_datetime(df_invoices["due_date"], errors="raise")
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Reference date and invoice due dates must be valid dates") from exc

    if pd.isna(ref_date) or due_dates.isna().any():
        raise ValueError("Reference date and invoice due dates cannot be missing")

    amounts = pd.to_numeric(df_invoices["amount"], errors="raise")
    if not np.isfinite(amounts.to_numpy(dtype=float)).all():
        raise ValueError("Invoice amounts must be finite numbers")
    if (amounts < 0).any():
        raise ValueError("Invoice amounts cannot be negative")

    statuses = df_invoices["status"]
    if statuses.isna().any() or statuses.astype(str).str.strip().eq("").any():
        raise ValueError("Invoice status cannot be missing or empty")

    # Compare calendar dates, not time-of-day.
    overdue_mask = (
        (due_dates.dt.normalize() < pd.Timestamp(ref_date).normalize())
        & (statuses.astype(str).str.strip().str.lower() != "paid")
    )
    result = df_invoices.loc[overdue_mask, ["invoice_id", "customer_id"]].copy()
    result["amount"] = amounts.loc[overdue_mask]
    result["due_date"] = due_dates.loc[overdue_mask]

    return {
        "overdue_count": int(len(result)),
        "total_overdue_amount": float(result["amount"].sum()),
        "overdue_invoices": result[["invoice_id", "customer_id", "amount", "due_date"]].to_dict(orient="records"),
    }



def calculate_burn_rate(df_transactions: pd.DataFrame, period_days: int = 30) -> Dict[str, float]:
    """Calculate average daily and 30-day outflow using a valid positive period."""
    if isinstance(period_days, bool) or not isinstance(period_days, (int, np.integer)) or period_days <= 0:
        raise ValueError("period_days must be a positive integer")
    if not isinstance(df_transactions, pd.DataFrame):
        raise ValueError("df_transactions must be a pandas DataFrame")

    if df_transactions.empty:
        outflows = 0.0
    else:
        tx = _validated_transactions(df_transactions)
        outflows = float(tx.loc[tx["transaction_type"] == "outflow", "amount"].sum())

    daily_burn = float(outflows / period_days)
    return {
        "daily_burn_rate": daily_burn,
        "monthly_burn_rate": float(daily_burn * 30),
    }



def calculate_sme_financial_health(
    inflow: float,
    outflow: float,
    cash_reserve: float
) -> Dict[str, Any]:
    """Calculate deterministic SME cash-flow indicators from finite nonnegative inputs."""
    inflow = _finite_number(inflow, "inflow")
    outflow = _finite_number(outflow, "outflow")
    cash_reserve = _finite_number(cash_reserve, "cash_reserve")
    if min(inflow, outflow, cash_reserve) < 0:
        raise ValueError("inflow, outflow, and cash_reserve cannot be negative")

    net_cash_flow = round(inflow - outflow, 2)
    operating_margin = round(net_cash_flow / inflow * 100, 2) if inflow > 0 else 0.0
    monthly_burn_rate = round(max(outflow - inflow, 0.0), 2)
    estimated_runway = (
        round(cash_reserve / monthly_burn_rate, 1)
        if monthly_burn_rate > 0 else None
    )

    return {
        "gross_inflow": inflow,
        "gross_outflow": outflow,
        "net_cash_flow": net_cash_flow,
        "operating_margin_pct": operating_margin,
        "monthly_burn_rate": monthly_burn_rate,
        "estimated_runway_months": estimated_runway,
        "health_status": "Healthy" if net_cash_flow >= 0 else "Liquidity Warning",
    }



def calculate_invoice_late_risk_score(
    invoice_amount: float,
    payment_terms_days: int,
    historical_late_count: int = 0
) -> Dict[str, Any]:
    """Compute a transparent rule-based heuristic; this is not a trained prediction."""
    invoice_amount = _finite_number(invoice_amount, "invoice_amount")
    if invoice_amount < 0:
        raise ValueError("invoice_amount cannot be negative")

    for name, value in (
        ("payment_terms_days", payment_terms_days),
        ("historical_late_count", historical_late_count),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, np.integer)) or value < 0:
            raise ValueError(f"{name} must be a nonnegative integer")

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
        "risk_level": risk_level,
    }
