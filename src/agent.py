"""
FinPilot AI — Core Copilot Agent Logic
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
            inflow = context_data.get("inflow", 150000) if context_data else 150000
            outflow = context_data.get("outflow", 110000) if context_data else 110000
            cash_reserve = context_data.get("cash_reserve", 200000) if context_data else 200000

            metrics = calculate_sme_financial_health(inflow, outflow, cash_reserve)
            return {
                "intent": "Financial Analytics",
                "status": "Success",
                "calculated_metrics": metrics,
                "response_summary": (
                    f"Financial Health Audit Completed. Net Cash Flow: {metrics['net_cash_flow']} BDT. "
                    f"Operating Margin: {metrics['operating_margin_pct']}%. Estimated Runway: {metrics['estimated_runway_months']} months."
                )
            }

        # 2. Policy & Refinance Regulation Route (RAG)
        else:
            retrieved_policies = self.rag_engine.query_policy(query, top_k=2)
            top_policy = retrieved_policies[0] if retrieved_policies else {}

            return {
                "intent": "Policy Information (RAG)",
                "status": "Success",
                "citations": [doc["source"] for doc in retrieved_policies],
                "retrieved_context": retrieved_policies,
                "response_summary": (
                    f"Grounded Policy Response: {top_policy.get('text', 'No policy matched.')} "
                    f"[Source Citation: {top_policy.get('source', 'N/A')}]"
                )
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