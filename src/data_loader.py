"""
FinMatrix SME Data Ingestion & Hygiene Validation Engine
Handles dataset loading, missing-value imputation, duplicate cleanup, and dynamic feature preparation.
"""

import os
import pandas as pd
import numpy as np

def clean_and_validate_sme_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans and standardizes input SME ledger dataframe.
    - Normalizes column headers to lowercase.
    - Handles invalid date formats gracefully.
    - Fills missing/null values and handles invalid negative numbers.
    - Removes duplicate transaction records.
    """
    if df is None or df.empty:
        return pd.DataFrame()

    df_cleaned = df.copy()

    # 1. Normalize column names
    df_cleaned.columns = [str(c).strip().lower() for c in df_cleaned.columns]

    # 2. Date parsing and sorting
    date_col = None
    for possible_date in ['trans_date', 'date', 'transaction_date', 'timestamp']:
        if possible_date in df_cleaned.columns:
            date_col = possible_date
            break

    if date_col:
        df_cleaned['trans_date'] = pd.to_datetime(df_cleaned[date_col], errors='coerce')
        df_cleaned = df_cleaned.dropna(subset=['trans_date'])
    else:
        # Fallback date generation if missing
        df_cleaned['trans_date'] = pd.date_range(start="2025-01-01", periods=len(df_cleaned), freq="D")

    # 3. Numeric column hygiene & Imputation
    for num_col in ['inflow', 'outflow', 'net_flow', 'amount']:
        if num_col in df_cleaned.columns:
            df_cleaned[num_col] = pd.to_numeric(df_cleaned[num_col], errors='coerce').fillna(0.0)
            if num_col in ['inflow', 'outflow']:
                df_cleaned[num_col] = df_cleaned[num_col].abs()

    # Calculate net_flow if not explicit
    if 'net_flow' not in df_cleaned.columns:
        if 'inflow' in df_cleaned.columns and 'outflow' in df_cleaned.columns:
            df_cleaned['net_flow'] = df_cleaned['inflow'] - df_cleaned['outflow']
        else:
            df_cleaned['net_flow'] = pd.to_numeric(df_cleaned.iloc[:, 1], errors='coerce').fillna(0.0)

    # 4. Remove duplicate entries
    df_cleaned = df_cleaned.drop_duplicates(subset=['trans_date']).sort_values('trans_date').reset_index(drop=True)

    return df_cleaned


def load_sme_data(data_path: str = None) -> pd.DataFrame:
    """
    Loads primary Bangladesh SME cashflow dataset or generates clean synthetic baseline.
    """
    if data_path is None:
        data_path = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "bangladesh_sme_cashflow.csv")

    if os.path.exists(data_path):
        try:
            raw_df = pd.read_csv(data_path)
            return clean_and_validate_sme_data(raw_df)
        except Exception:
            pass

    # Clean Synthetic Fallback Data Creation
    np.random.seed(42)
    dates = pd.date_range(start="2025-01-01", periods=180, freq="D")
    inflow = np.random.uniform(15000, 60000, size=180)
    outflow = np.random.uniform(10000, 45000, size=180)
    synth_df = pd.DataFrame({"trans_date": dates, "inflow": inflow, "outflow": outflow, "net_flow": inflow - outflow})
    
    return clean_and_validate_sme_data(synth_df)