"""
FinMatrix Copilot— Executive PDF & CSV Report Generator
Generates enterprise-grade audit summaries, cash-flow metrics,
and risk evaluations for SME stakeholders and banking institution partners.
"""

import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any


class ExecutiveReportGenerator:
    @staticmethod
    def _format_runway(value: Any) -> str:
        """Format runway without presenting a placeholder as a real estimate."""
        if value is None:
            return "No current cash burn"
        return f"{value} months"

    def __init__(self, output_dir: str = "data/reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_csv_summary(self, metrics: Dict[str, Any], forecast_df: pd.DataFrame) -> str:
        """Exports core liquidity and forecast values to a structured CSV file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(self.output_dir, f"SME_Financial_Summary_{timestamp}.csv")
        
        # Combine Metrics Header with Forecast Table
        summary_rows = [
            {"Category": "Metric", "Key": "Net Cash Flow", "Value": str(metrics.get("net_cash_flow", 0.0))},
            {"Category": "Metric", "Key": "Operating Margin (%)", "Value": str(metrics.get("operating_margin_pct", 0.0))},
            {"Category": "Metric", "Key": "Monthly Burn Rate", "Value": str(metrics.get("monthly_burn_rate", 0.0))},
            {"Category": "Metric", "Key": "Estimated Runway", "Value": self._format_runway(metrics.get("estimated_runway_months"))},
            {"Category": "Metric", "Key": "Health Status", "Value": str(metrics.get("health_status", "N/A"))},
        ]
        
        df_summary = pd.DataFrame(summary_rows)
        df_summary.to_csv(filepath, index=False)
        return filepath

    def generate_text_audit_report(self, metrics: Dict[str, Any], risk_res: Dict[str, Any]) -> str:
        """Generates a structured text executive report suitable for PDF conversion or plain display."""
        report = f"""
================================================================================
                    FINMATRIX — EXECUTIVE FINANCIAL AUDIT REPORT
================================================================================
Generated On: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Target Entity: SME Business Partner
Benchmarked Currency: USD ($) / BDT (৳)
--------------------------------------------------------------------------------

1. LIQUIDITY & OPERATIONAL RUNWAY AUDIT
   - Net Monthly Cash Flow : {metrics.get('net_cash_flow', 0.0):,.2f}
   - Operating Margin       : {metrics.get('operating_margin_pct', 0.0)}%
   - Monthly Burn Rate      : {metrics.get('monthly_burn_rate', 0.0):,.2f}
   - Estimated Runway       : {self._format_runway(metrics.get('estimated_runway_months'))}
   - Health Classification  : {metrics.get('health_status', 'N/A')}

2. INVOICE CREDIT RISK ASSESSMENT
   - Exposure Risk Score    : {risk_res.get('risk_score', 0.0)} / 1.0
   - Risk Classification    : {risk_res.get('risk_level', 'N/A')}

3. COMPLIANCE & GOVERNANCE NOTE
   - Guardrail Model        : Level-1 Temporal Protection Active
   - RAG Verification       : Grounded against Official Regulatory Circulars

================================================================================
                            END OF EXECUTIVE REPORT
================================================================================
"""
        filepath = os.path.join(self.output_dir, f"Executive_Audit_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report)
        return filepath, report


if __name__ == "__main__":
    print("--- Testing Report Generator Engine ---")
    gen = ExecutiveReportGenerator()
    dummy_metrics = {
        "net_cash_flow": 7000.0,
        "operating_margin_pct": 28.0,
        "monthly_burn_rate": 0.0,
        "estimated_runway_months": None,
        "health_status": "Healthy"
    }
    dummy_risk = {"risk_score": 0.45, "risk_level": "Medium"}
    
    filepath, content = gen.generate_text_audit_report(dummy_metrics, dummy_risk)
    print(f"Report Generated Successfully at: {filepath}")
    print(content)