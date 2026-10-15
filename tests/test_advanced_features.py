"""
FinMatrix Copilot — Test Suite for Data Loader, Audit Logger, and Report Generator
Ensures 100% reliability for advanced enterprise modules under Pytest.
"""

import os
import pandas as pd
import pytest
from src.data_loader import SMEDataLoader
from src.audit_logger import AuditLogger
from src.report_generator import ExecutiveReportGenerator


def test_data_loader_cleaning():
    loader = SMEDataLoader()
    sample_data = pd.DataFrame({
        "Invoice_No": ["INV-001", "INV-001"],
        "Total": [5000.0, 5000.0],
        "Trans_Date": ["2026-01-10", "2026-01-10"]
    })
    
    test_path = "tests/temp_test.csv"
    sample_data.to_csv(test_path, index=False)
    
    with open(test_path, "rb") as f:
        cleaned_df, audit = loader.load_and_validate_file(f, "temp_test.csv")
        
    assert audit["raw_rows"] == 2
    assert audit["cleaned_rows"] == 1
    assert audit["duplicates_removed"] == 1
    
    if os.path.exists(test_path):
        os.remove(test_path)


def test_audit_logger_persistence():
    test_log_path = "tests/temp_audit.json"
    logger = AuditLogger(log_filepath=test_log_path)
    
    entry = logger.log_event("Pytest System Check", status="Approved")
    all_logs = logger.get_all_logs()
    
    assert len(all_logs) >= 2
    assert entry["event"] == "Pytest System Check"
    assert entry["status"] == "Approved"
    
    if os.path.exists(test_log_path):
        os.remove(test_log_path)


def test_report_generator():
    test_dir = "tests/temp_reports"
    gen = ExecutiveReportGenerator(output_dir=test_dir)
    
    dummy_metrics = {"net_cash_flow": 5000.0, "operating_margin_pct": 20.0}
    dummy_risk = {"risk_score": 0.2, "risk_level": "Low"}
    
    filepath, content = gen.generate_text_audit_report(dummy_metrics, dummy_risk)
    
    assert os.path.exists(filepath)
    assert "FINPILOT AI — EXECUTIVE FINANCIAL AUDIT REPORT" in content
    
    if os.path.exists(filepath):
        os.remove(filepath)
    if os.path.exists(test_dir):
        os.rmdir(test_dir)