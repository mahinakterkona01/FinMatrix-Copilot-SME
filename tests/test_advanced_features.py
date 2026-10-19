
"""
FinMatrix Copilot - Test Suite for Data Loader, Audit Logger,
and Report Generator.

Tests the current data-cleaning function and verifies that
audit logging and report generation work as expected.
"""

import os

import pandas as pd

from src.data_loader import clean_and_validate_sme_data
from src.audit_logger import AuditLogger
from src.report_generator import ExecutiveReportGenerator
from src.agent import SMEFinanceAgent


def test_data_loader_cleaning():
    """Test column normalization, date parsing, and duplicate removal."""

    sample_data = pd.DataFrame({
        "Invoice_No": ["INV-001", "INV-001"],
        "Total": [5000.0, 5000.0],
        "Trans_Date": ["2026-01-10", "2026-01-10"]
    })

    cleaned_df = clean_and_validate_sme_data(sample_data)

    # Check that column names are normalized.
    assert "invoice_no" in cleaned_df.columns
    assert "total" in cleaned_df.columns

    # Check that the standardized date column exists.
    assert "trans_date" in cleaned_df.columns

    # The current implementation removes duplicate transaction dates.
    assert len(cleaned_df) == 1

    # Check that the remaining date is valid.
    assert pd.notna(cleaned_df.iloc[0]["trans_date"])

        # No financial flow columns are present, so net_flow
    # must not be fabricated from an unrelated column.
    assert "net_flow" not in cleaned_df.columns


def test_audit_logger_persistence():
    """Test that audit events are written and can be retrieved."""

    test_log_path = "tests/temp_audit.json"

    try:
        logger = AuditLogger(log_filepath=test_log_path)

        entry = logger.log_event(
            "Pytest System Check",
            status="Approved"
        )

        all_logs = logger.get_all_logs()

        assert isinstance(all_logs, list)
        assert len(all_logs) >= 1
        assert entry["event"] == "Pytest System Check"
        assert entry["status"] == "Approved"

        # Confirm that the log file was created.
        assert os.path.exists(test_log_path)

    finally:
        if os.path.exists(test_log_path):
            os.remove(test_log_path)


def test_report_generator():
    """Test that an executive financial audit report is generated."""

    test_dir = "tests/temp_reports"

    dummy_metrics = {
        "net_cash_flow": 5000.0,
        "operating_margin_pct": 20.0
    }

    dummy_risk = {
        "risk_score": 0.2,
        "risk_level": "Low"
    }

    try:
        generator = ExecutiveReportGenerator(output_dir=test_dir)

        filepath, content = generator.generate_text_audit_report(
            dummy_metrics,
            dummy_risk
        )

        assert os.path.exists(filepath)
        assert isinstance(content, str)
        assert len(content) > 0

        # Verify that the report includes the supplied financial metrics.
        assert "5,000.00" in content
        assert "20.0%" in content
        assert "0.2 / 1.0" in content
        assert "Low" in content

    finally:
        if os.path.exists(test_dir):
            for filename in os.listdir(test_dir):
                file_path = os.path.join(test_dir, filename)

                if os.path.isfile(file_path):
                    os.remove(file_path)

            if not os.listdir(test_dir):
                os.rmdir(test_dir)


def test_agent_reports_no_current_cash_burn_without_fake_runway():
    agent = SMEFinanceAgent()
    result = agent.process_query(
        "Check my financial health and runway",
        {"inflow": 200000, "outflow": 150000, "cash_reserve": 300000},
    )

    assert "No current cash burn" in result["response_summary"]
    assert "999 months" not in result["response_summary"]
    assert "None months" not in result["response_summary"]


def test_agent_reports_numeric_runway_when_cash_flow_is_negative():
    agent = SMEFinanceAgent()
    result = agent.process_query(
        "Check my financial health and runway",
        {"inflow": 100000, "outflow": 150000, "cash_reserve": 100000},
    )

    assert "2.0 months" in result["response_summary"]
    assert "None months" not in result["response_summary"]


def test_agent_requires_real_context_before_financial_calculation():
    agent = SMEFinanceAgent()
    result = agent.process_query("Check my financial health and runway")

    assert result["status"] == "Needs Data"
    assert result["calculated_metrics"] is None
    assert set(result["missing_fields"]) == {
        "inflow", "outflow", "cash_reserve"
    }
    assert "assumed" in result["response_summary"].lower()


def test_agent_rejects_invalid_financial_inputs():
    agent = SMEFinanceAgent()
    result = agent.process_query(
        "Check my financial health",
        {"inflow": float("nan"), "outflow": 100, "cash_reserve": 500},
    )

    assert result["status"] == "Invalid Data"
    assert result["calculated_metrics"] is None


def test_agent_labels_retrieved_policy_as_unverified_evidence(monkeypatch):
    agent = SMEFinanceAgent()
    retrieved = [{
        "source": "example_circular.pdf",
        "section": "page-1",
        "text": "Eligible SMEs may apply under the stated facility.",
        "effective_date": None,
        "relevance_score": 0.54,
    }]
    monkeypatch.setattr(
        agent.rag_engine,
        "query_policy",
        lambda query, top_k=2: retrieved,
    )

    result = agent.process_query(
        "What is the current SME loan interest rate?"
    )
    summary = result["response_summary"].lower()

    assert result["status"] == "Evidence Retrieved (Unverified)"
    assert result["citations"] == ["example_circular.pdf"]
    assert "not a confirmed answer" in summary
    assert "does not establish" in summary
    assert "effective date: not verified" in summary
    assert "eligible smes may apply" in summary


def test_agent_treats_empty_retrieved_excerpts_as_no_match(monkeypatch):
    agent = SMEFinanceAgent()
    monkeypatch.setattr(
        agent.rag_engine,
        "query_policy",
        lambda query, top_k=2: [
            {"source": "empty.pdf", "text": "   "}
        ],
    )

    result = agent.process_query("Tell me the applicable SME policy.")

    assert result["status"] == "No Match"
    assert result["citations"] == []
    assert result["retrieved_context"] == []
    assert "cannot confirm" in result["response_summary"].lower()


def test_agent_reports_no_match_when_policy_retrieval_is_empty(monkeypatch):
    agent = SMEFinanceAgent()
    monkeypatch.setattr(
        agent.rag_engine, "query_policy", lambda query, top_k=2: []
    )

    result = agent.process_query(
        "What policy applies to an unrelated question?"
    )

    assert result["status"] == "No Match"
    assert result["citations"] == []
    assert result["retrieved_context"] == []
    assert "cannot confirm" in result["response_summary"].lower()
