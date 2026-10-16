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
        raise ValueError(
            "No supported date column found. Expected one of: "
            "trans_date, date, transaction_date, timestamp."
        )
    # 3. Numeric column hygiene & Imputation
    for num_col in ['inflow', 'outflow', 'net_flow', 'amount']:
        if num_col in df_cleaned.columns:
            df_cleaned[num_col] = pd.to_numeric(df_cleaned[num_col], errors='coerce').fillna(0.0)
            if num_col in ['inflow', 'outflow']:
                df_cleaned[num_col] = df_cleaned[num_col].abs()

   
    # 3. Calculate financial flows using recognized columns only.
    if "net_flow" not in df_cleaned.columns:
        if {"inflow", "outflow"}.issubset(df_cleaned.columns):
            df_cleaned["net_flow"] = (
                df_cleaned["inflow"] - df_cleaned["outflow"]
            )

        elif {"amount", "transaction_type"}.issubset(df_cleaned.columns):
            transaction_types = (
                df_cleaned["transaction_type"]
                .astype("string")
                .str.strip()
                .str.lower()
            )

            inflow_mask = transaction_types.isin(
                ["inflow", "income", "credit", "receipt"]
            )
            outflow_mask = transaction_types.isin(
                ["outflow", "expense", "debit", "payment"]
            )

            unknown_mask = ~(inflow_mask | outflow_mask)

            if unknown_mask.any():
                unknown_types = (
                    transaction_types[unknown_mask]
                    .dropna()
                    .unique()
                    .tolist()
                )
                raise ValueError(
                    "Unknown transaction types; cannot calculate "
                    f"net_flow safely: {unknown_types}"
                )

            df_cleaned["inflow"] = df_cleaned["amount"].where(
                inflow_mask, 0.0
            )
            df_cleaned["outflow"] = df_cleaned["amount"].where(
                outflow_mask, 0.0
            )
            df_cleaned["net_flow"] = (
                df_cleaned["inflow"] - df_cleaned["outflow"]
            )


    # 4. Remove exact duplicate records only.
    # Multiple legitimate transactions may occur on the same date.
    df_cleaned = (
        df_cleaned
        .drop_duplicates()
        .sort_values("trans_date")
        .reset_index(drop=True)
    )

    return df_cleaned

def load_sme_data(data_path: str = None) -> pd.DataFrame:
    """
    Load and validate the configured SME cash-flow dataset.

    Missing or unreadable files raise an explicit error instead of
    silently substituting unrelated synthetic data.
    """
    if data_path is None:
        data_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "raw",
            "bangladesh_sme_cashflow.csv",
        )

    if not os.path.isfile(data_path):
        raise FileNotFoundError(
            f"SME dataset not found: {data_path}. "
            "Please provide a valid dataset path."
        )

    try:
        raw_df = pd.read_csv(data_path)
    except (OSError, UnicodeError, pd.errors.ParserError) as exc:
        raise ValueError(
            f"Could not read SME dataset '{data_path}': {exc}"
        ) from exc

    if raw_df.empty:
        raise ValueError(
            f"SME dataset is empty: {data_path}"
        )

    cleaned_df = clean_and_validate_sme_data(raw_df)

    
    if cleaned_df.empty:
        raise ValueError(
            f"No valid records remain after cleaning: {data_path}"
        )

    # Forecasting requires a valid financial target.
    if "net_flow" not in cleaned_df.columns:
        raise ValueError(
            "The dataset does not contain usable cash-flow data. "
            "Expected either inflow and outflow columns, or amount "
            "and transaction_type columns that can produce net_flow."
        )

    return cleaned_df


