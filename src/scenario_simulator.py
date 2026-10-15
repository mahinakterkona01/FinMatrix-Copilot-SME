"""
FinPilot AI — What-If Scenario Simulation Engine
Allows SMEs to simulate financial impacts of delayed payments, revenue drops,
or sudden expense increases on projected cash balances.
"""

from typing import Dict, Any
import pandas as pd


def simulate_delayed_receivable(
    current_balance: float,
    projected_inflows: float,
    projected_outflows: float,
    delayed_inflow_amount: float
) -> Dict[str, Any]:
    """
    Simulates the impact on ending cash balance if a specific customer payment is delayed.
    """
    baseline_ending_balance = current_balance + projected_inflows - projected_outflows
    simulated_inflows = max(0.0, projected_inflows - delayed_inflow_amount)
    simulated_ending_balance = current_balance + simulated_inflows - projected_outflows

    net_impact = simulated_ending_balance - baseline_ending_balance

    return {
        "scenario_type": "delayed_receivable",
        "current_balance": float(current_balance),
        "delayed_amount": float(delayed_inflow_amount),
        "baseline_ending_balance": float(baseline_ending_balance),
        "simulated_ending_balance": float(simulated_ending_balance),
        "net_impact": float(net_impact),
        "causes_deficit": bool(simulated_ending_balance < 0.0)
    }


def simulate_expense_surge(
    current_balance: float,
    projected_inflows: float,
    projected_outflows: float,
    expense_increase_percentage: float
) -> Dict[str, Any]:
    """
    Simulates the impact of a percentage increase in operational expenses.
    """
    baseline_ending_balance = current_balance + projected_inflows - projected_outflows
    multiplier = 1.0 + (expense_increase_percentage / 100.0)
    simulated_outflows = projected_outflows * multiplier
    simulated_ending_balance = current_balance + projected_inflows - simulated_outflows

    return {
        "scenario_type": "expense_surge",
        "expense_increase_percentage": float(expense_increase_percentage),
        "baseline_outflows": float(projected_outflows),
        "simulated_outflows": float(simulated_outflows),
        "baseline_ending_balance": float(baseline_ending_balance),
        "simulated_ending_balance": float(simulated_ending_balance),
        "causes_deficit": bool(simulated_ending_balance < 0.0)
    }