"""
FinMatrix Copilot— Core Copilot Agent Logic
Orchestrates deterministic financial calculations, cash-flow forecasting,
and citation-grounded policy RAG for SME financial query handling.
"""

from typing import Dict, Any
from src.financial_tools import calculate_sme_financial_health
from src.retrieval import PolicyRAGEngine


class SMEFinanceAgent:
    def __init__(self):
        self.rag_engine = PolicyRAGEngine()
        self.rag_engine.build_index()

    def process_query(self, query: str, context_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Routes user query through deterministic financial logic or policy RAG retrieval.
        """
        query_lower = query.lower()

        # 1. Financial Health & Ledger Analytics Route
        if any(keyword in query_lower for keyword in ["health", "ratio", "cashflow", "runway", "burn"]):
            required_fields = ("inflow", "outflow", "cash_reserve")
            if not isinstance(context_data, dict):
                context_data = {}

            missing_fields = [
                field for field in required_fields
                if context_data.get(field) is None
            ]
            if missing_fields:
                readable = ", ".join(missing_fields)
                return {
                    "intent": "Financial Analytics",
                    "status": "Needs Data",
                    "calculated_metrics": None,
                    "missing_fields": missing_fields,
                    "response_summary": (
                        "I cannot calculate financial health or cash runway yet. "
                        f"Please provide these values: {readable}. "
                        "No financial figures have been assumed."
                    ),
                }

            try:
                inflow, outflow, cash_reserve = (
                    float(context_data[field]) for field in required_fields
                )
            except (TypeError, ValueError, OverflowError):
                return {
                    "intent": "Financial Analytics",
                    "status": "Invalid Data",
                    "calculated_metrics": None,
                    "response_summary": (
                        "Financial inputs must be valid numeric values. "
                        "Please check inflow, outflow, and cash reserve."
                    ),
                }

            import math
            if (
                not all(math.isfinite(value) for value in
                        (inflow, outflow, cash_reserve))
                or min(inflow, outflow, cash_reserve) < 0
            ):
                return {
                    "intent": "Financial Analytics",
                    "status": "Invalid Data",
                    "calculated_metrics": None,
                    "response_summary": (
                        "Financial inputs must be finite, non-negative numbers. "
                        "Please correct the values and try again."
                    ),
                }

            metrics = calculate_sme_financial_health(inflow, outflow, cash_reserve)
            runway = metrics["estimated_runway_months"]
            runway_text = (
                f"{runway} months"
                if runway is not None
                else "No current cash burn"
            )
            return {
                "intent": "Financial Analytics",
                "status": "Success",
                "calculated_metrics": metrics,
                "response_summary": (
                    f"Financial Health Audit Completed. Net Cash Flow: {metrics['net_cash_flow']} (currency not specified). "
                    f"Operating Margin: {metrics['operating_margin_pct']}%. Estimated Runway: {runway_text}."
                )
            }

        # 2. Policy & Refinance Regulation Route (RAG)
        else:
            retrieved_policies = self.rag_engine.query_policy(query, top_k=2)
            if not retrieved_policies:
                return {
                    "intent": "Policy Information (RAG)",
                    "status": "No Match",
                    "citations": [],
                    "retrieved_context": [],
                    "response_summary": (
                        "I could not find a relevant policy in the available "
                        "indexed documents. I cannot confirm an answer from "
                        "the current knowledge base."
                    ),
                }

            usable_evidence = [
                doc for doc in retrieved_policies
                if isinstance(doc.get("text"), str) and doc["text"].strip()
            ]
            if not usable_evidence:
                return {
                    "intent": "Policy Information (RAG)",
                    "status": "No Match",
                    "citations": [],
                    "retrieved_context": [],
                    "response_summary": (
                        "The retrieval system returned no usable policy excerpts. "
                        "I cannot confirm the requested policy details."
                    ),
                }

            citations = [
                doc["source"] for doc in usable_evidence if doc.get("source")
            ]
            evidence_lines = []
            for doc in usable_evidence:
                source = doc.get("source") or "Source unavailable"
                section = doc.get("section") or "Section unavailable"
                effective_date = doc.get("effective_date") or "Not verified"
                score = doc.get("relevance_score")
                score_text = (
                    f"{score}" if isinstance(score, (int, float))
                    else "Not available"
                )
                evidence_lines.append(
                    f"[Source: {source}; Section: {section}; "
                    f"Effective date: {effective_date}; "
                    f"Retrieval relevance score: {score_text}]\n"
                    f"{doc['text'].strip()}"
                )

            return {
                "intent": "Policy Information (RAG)",
                "status": "Evidence Retrieved (Unverified)",
                "citations": citations,
                "retrieved_context": usable_evidence,
                "response_summary": (
                    "I found potentially relevant policy excerpt(s), but these "
                    "are not a confirmed answer to your question. Retrieval "
                    "relevance does not establish that a document is official, "
                    "current, or legally applicable. Verify the original "
                    "circular, effective date, and amendments before making a "
                    "financial decision.\n\n"
                    + "\n\n".join(evidence_lines)
                ),
            }


if __name__ == "__main__":
    print("--- Running Copilot Agent Logic Verification ---")
    agent = SMEFinanceAgent()

    # Test 1: Financial Health Calculation Query
    q1 = "Check my current SME financial health and cash runway"
    res1 = agent.process_query(q1, {"inflow": 250000, "outflow": 180000, "cash_reserve": 350000})
    print(f"\n[Test 1 Query]: {q1}")
    print(f"Response: {res1['response_summary']}")

    # Test 2: Bangladesh Bank Policy Query
    q2 = "What is the interest rate and facility for working capital refinance?"
    res2 = agent.process_query(q2)
    print(f"\n[Test 2 Query]: {q2}")
    print(f"Response: {res2['response_summary']}")
    print(f"Citations: {res2['citations']}")