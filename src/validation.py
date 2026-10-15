"""
FinMatrix Copilot— Data Ingestion & Quality Validation Engine
Enforces schema validation, data provenance tagging, and data quality checks
for SME financial transaction and invoice records.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Tuple
import pandas as pd


class DataSourceType(Enum):
    REAL_SME_INTERNAL = "real_sme_internal"
    REAL_EXTERNAL_BARNET = "real_external_barnet"
    MACRO_BANGLADESH_BANK = "macro_bangladesh_bank"
    SYNTHETIC_SIMULATED = "synthetic_simulated"


@dataclass
class DataProvenance:
    dataset_name: str
    source_type: DataSourceType
    source_url: str
    licence: str
    is_synthetic: bool
    observation_unit: str


REQUIRED_CASHFLOW_COLUMNS = ["transaction_id", "date", "amount", "transaction_type"]
REQUIRED_INVOICE_COLUMNS = ["invoice_id", "customer_id", "issue_date", "due_date", "amount", "status"]


def validate_sme_cashflow_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates required columns, data types, and missing values for cash flow data.
    """
    errors = []
    missing_cols = [col for col in REQUIRED_CASHFLOW_COLUMNS if col not in df.columns]
    
    if missing_cols:
        errors.append(f"Missing mandatory cash flow columns: {missing_cols}")
        return False, errors

    if df["amount"].isnull().any():
        errors.append("Dataset contains missing values in mandatory 'amount' field.")

    if not pd.api.types.is_numeric_dtype(df["amount"]):
        errors.append("'amount' column must be numeric.")

    return len(errors) == 0, errors


def validate_invoice_schema(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates required columns and checks for duplicate invoice IDs.
    """
    errors = []
    missing_cols = [col for col in REQUIRED_INVOICE_COLUMNS if col not in df.columns]
    
    if missing_cols:
        errors.append(f"Missing mandatory invoice columns: {missing_cols}")
        return False, errors

    if df["invoice_id"].duplicated().any():
        dup_count = int(df["invoice_id"].duplicated().sum())
        errors.append(f"Detected {dup_count} duplicate invoice IDs.")

    return len(errors) == 0, errors


def add_provenance_metadata(df: pd.DataFrame, provenance: DataProvenance) -> pd.DataFrame:
    """
    Appends mandatory data provenance tracking fields to dataframe.
    """
    df_tagged = df.copy()
    df_tagged["_source_dataset"] = provenance.dataset_name
    df_tagged["_source_type"] = provenance.source_type.value
    df_tagged["_is_synthetic"] = provenance.is_synthetic
    return df_tagged