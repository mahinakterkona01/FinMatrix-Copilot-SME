
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
