from src.agent import SMEFinanceAgent
def test_financial_agent_does_not_assume_bdt_currency():
    from src.agent import SMEFinanceAgent

    agent = SMEFinanceAgent.__new__(SMEFinanceAgent)
    result = agent.process_query(
        "Check my financial health and cash runway",
        {"inflow": 250000, "outflow": 180000, "cash_reserve": 350000},
    )

    assert result["status"] == "Success"
    assert "currency not specified" in result["response_summary"].lower()
    assert "BDT" not in result["response_summary"]
