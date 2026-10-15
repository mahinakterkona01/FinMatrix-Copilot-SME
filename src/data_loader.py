"""
FinPilot AI — Data Ingestion & Validation Engine
Handles file parsing (CSV/Excel), schema mapping, quality audits,
missing value handling, and duplicate detection for SME transaction logs.
"""

import os
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any


class SMEDataLoader:
    def __init__(self):
        self.supported_extensions = [".csv", ".xlsx", ".xls"]

    def load_and_validate_file(self, file_buffer, file_name: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Parses CSV/Excel file, executes quality audit, and cleans records.
        """
        ext = os.path.splitext(file_name)[1].lower()
        if ext not in self.supported_extensions:
            raise ValueError(f"Unsupported file format: {ext}. Upload CSV or Excel files.")

        # 1. Parse File
        if ext == ".csv":
            df = pd.read_csv(file_buffer)
        else:
            df = pd.read_excel(file_buffer)

        raw_rows = len(df)
        
        # 2. Quality Audit
        initial_missing = int(df.isnull().sum().sum())
        initial_duplicates = int(df.duplicated().sum())

        # 3. Standardize Columns (Lowercase & Strip)
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

        # 4. Auto-Mapping Common Column Names
        column_mapping = {
            "invoice_no": "invoice_id",
            "inv_id": "invoice_id",
            "trans_type": "transaction_type",
            "type": "transaction_type",
            "val": "amount",
            "total": "amount",
            "trans_date": "date",
            "created_at": "date"
        }
        df = df.rename(columns=column_mapping)

        # 5. Data Cleaning & Validation
        df = df.drop_duplicates().reset_index(drop=True)
        
        # Fill missing text with 'Unknown' and numeric with 0.0
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("Unknown")
            else:
                df[col] = df[col].fillna(0.0)

        # Validate Date format if present
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")
            df["date"] = df["date"].fillna("2026-01-01")

        cleaned_rows = len(df)

        audit_summary = {
            "file_name": file_name,
            "raw_rows": raw_rows,
            "cleaned_rows": cleaned_rows,
            "duplicates_removed": initial_duplicates,
            "missing_values_handled": initial_missing,
            "columns": list(df.columns)
        }

        return df, audit_summary


if __name__ == "__main__":
    print("--- Running SME Data Loader Verification ---")
    loader = SMEDataLoader()
    
    # Inline Dummy Dataset Verification
    sample_data = pd.DataFrame({
        "Invoice_No": ["INV-001", "INV-002", "INV-001", "INV-003"],
        "Type": ["Inflow", "Outflow", "Inflow", "Inflow"],
        "Total": [5000.0, 2000.0, 5000.0, None],
        "Trans_Date": ["2026-01-10", "2026-01-11", "2026-01-10", "2026-01-12"]
    })
    
    sample_data.to_csv("data/raw/temp_test.csv", index=False)
    
    with open("data/raw/temp_test.csv", "rb") as f:
        cleaned_df, audit = loader.load_and_validate_file(f, "temp_test.csv")
        
    print("Audit Summary:", audit)
    print("\nCleaned Output Table:")
    print(cleaned_df)
    
    if os.path.exists("data/raw/temp_test.csv"):
        os.remove("data/raw/temp_test.csv")