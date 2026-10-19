import numpy as np
import pandas as pd


COLUMN_ALIASES = {
    "trans_date": [
        "trans_date", "transaction_date", "date", "txn_date", "payment_date"
    ],
    "inflow": [
        "inflow", "cash_inflow", "income", "revenue", "credit", "money_in"
    ],
    "outflow": [
        "outflow", "cash_outflow", "expense", "expenses", "debit", "money_out"
    ],
    "net_flow": [
        "net_flow", "netflow", "net_cash_flow", "net_amount"
    ],
    "amount": ["amount", "transaction_amount", "value"],
    "direction": ["direction", "type", "transaction_type", "flow_type"],
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize financial columns and validate numeric cash-flow values."""
    if df is None or df.empty:
        raise ValueError("The uploaded file has no data rows.")

    out = df.copy()
    out.columns = [
        str(c).strip().lower().replace(" ", "_").replace("-", "_")
        for c in out.columns
    ]

    rename = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        if canonical in out.columns:
            continue
        for alias in aliases:
            if alias in out.columns:
                rename[alias] = canonical
                break
    out = out.rename(columns=rename)

    if "trans_date" in out.columns:
        out["trans_date"] = pd.to_datetime(
            out["trans_date"], errors="coerce"
        )

    currency_symbols = ("$", "\u09f3", "\u20ac", "\u00a3", "\u00a5")

    for col in ("inflow", "outflow", "net_flow", "amount"):
        if col not in out.columns:
            continue

        cleaned = out[col].astype("string").str.strip()
        cleaned = cleaned.str.replace(",", "", regex=False)

        for symbol in currency_symbols:
            cleaned = cleaned.str.replace(symbol, "", regex=False)

        out[col] = pd.to_numeric(cleaned.str.strip(), errors="coerce")

    if {"inflow", "outflow"}.issubset(out.columns):
        invalid = out[["inflow", "outflow"]].isna().any(axis=1)
        if invalid.any():
            raise ValueError(
                f"{int(invalid.sum())} row(s) have missing or invalid "
                "inflow/outflow values."
            )

        if (out[["inflow", "outflow"]] < 0).any().any():
            raise ValueError(
                "Inflow and outflow must be non-negative. "
                "Use a direction/type column for signed transactions."
            )

        out["net_flow"] = out["inflow"] - out["outflow"]

    elif "net_flow" in out.columns:
        if out["net_flow"].isna().any():
            raise ValueError(
                f"{int(out['net_flow'].isna().sum())} row(s) have invalid "
                "net_flow values."
            )

    elif {"amount", "direction"}.issubset(out.columns):
        if out["amount"].isna().any():
            raise ValueError(
                "The amount column contains missing or invalid values."
            )

        direction = out["direction"].astype("string").str.strip().str.lower()
        inflow_labels = {
            "in", "inflow", "income", "revenue", "credit", "deposit", "receipt"
        }
        outflow_labels = {
            "out", "outflow", "expense", "debit", "withdrawal", "payment"
        }

        unknown = ~direction.isin(inflow_labels | outflow_labels)
        if unknown.any():
            vals = ", ".join(
                direction[unknown].dropna().drop_duplicates().head(5).tolist()
            )
            raise ValueError(
                f"Unrecognized transaction direction(s): {vals}. "
                "Use inflow/outflow labels."
            )

        out["inflow"] = np.where(
            direction.isin(inflow_labels), out["amount"], 0.0
        )
        out["outflow"] = np.where(
            direction.isin(outflow_labels), out["amount"], 0.0
        )
        out["net_flow"] = out["inflow"] - out["outflow"]

    else:
        raise ValueError(
            "Could not identify financial columns. Provide either inflow + "
            "outflow, a signed net_flow column, or amount + direction/type."
        )

    return out
