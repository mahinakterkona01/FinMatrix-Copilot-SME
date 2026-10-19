"""
FinMatrix Copilot— Security Sandbox & Permission Gatekeeper
Enforces input sanitization, prompt injection detection, hardcoded permission boundaries,
and Human-in-the-Loop (HITL) authorization for financial workflows.
"""

import re
from typing import Dict, Any, Tuple, List


# Known prompt injection attack signatures
INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?(?:previous|above)\s+instructions",
    r"system\s*:\s*override",
    r"transfer\s+all\s+funds",
    r"grant\s+admin",
    r"bypass\s+approval",
    r"reveal\s+secret",
    r"sudo\s+",
    r"eval\s*\(",
    r"\bdrop\s+table\b",
    r"\bartificially\s+inflate\b",
]


def sanitize_text_input(user_input: str) -> Tuple[str, bool, List[str]]:
    """
    Strips HTML markup, then scans the resulting text for potential
    prompt injection patterns.
    Returns sanitized text, injection detected flag, and triggered rules.
    """
    text = str(user_input).strip()

    # Strip HTML-like markup before scanning to detect tag-obfuscated phrases.
    sanitized_text = re.sub(r"<[^>]*>", "", text)

    triggered_rules = []
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, sanitized_text, re.IGNORECASE):
            triggered_rules.append(f"Prompt injection pattern matched: '{pattern}'")

    is_threat = len(triggered_rules) > 0
    return sanitized_text, is_threat, triggered_rules


def check_action_permission(
    action_name: str,
    requires_hitl: bool = True,
    is_hitl_approved: bool = False
) -> Dict[str, Any]:
    """
    Enforces authorization check before executing any side-effecting financial tool.
    """
    SAFE_READONLY_ACTIONS = [
        "calculate_cash_position",
        "detect_overdue_invoices",
        "calculate_burn_rate",
        "forecast_naive_baseline",
        "simulate_delayed_receivable",
        "simulate_expense_surge",
        "retrieve_relevant_documents"
    ]

    CONSEQUENTIAL_ACTIONS = [
        "create_payment_reminder",
        "draft_financing_application",
        "commit_scenario_plan"
    ]

    if action_name in SAFE_READONLY_ACTIONS:
        return {
            "action": action_name,
            "permitted": True,
            "reason": "ReadOnly action pre-approved.",
            "hitl_status": "Not Required"
        }

    if action_name in CONSEQUENTIAL_ACTIONS:
        if requires_hitl and not is_hitl_approved:
            return {
                "action": action_name,
                "permitted": False,
                "reason": "Consequential action blocked: Explicit Human-in-the-Loop (HITL) approval required.",
                "hitl_status": "Pending Approval"
            }
        return {
            "action": action_name,
            "permitted": True,
            "reason": "Consequential action approved by user.",
            "hitl_status": "Approved"
        }

    return {
        "action": action_name,
        "permitted": False,
        "reason": f"Unknown or unmapped action '{action_name}'. Default deny enforced.",
        "hitl_status": "Denied"
    }