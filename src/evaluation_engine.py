"""
FinMatrix Copilot ? Evaluation Engine & Level 1 Temporal ML Validation
Enhanced for Noise Robustness (Rolling Medians, Robust Scaling) & Temporal Leakage Prevention.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error, precision_score, recall_score, precision_recall_curve, auc
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from src.data_loader import load_sme_data


def evaluate_temporal_cashflow_forecasting(
    df_cashflow: pd.DataFrame,
    train_ratio: float = 0.8
) -> Dict[str, Any]:
    """
    Level 1 Temporal Validation for Cash Flow Forecasting.
    Includes Robust Features (Rolling Medians) to handle noisy SME transactions.
    """
    if not 0.0 < train_ratio < 1.0:
        raise ValueError("train_ratio must be strictly between 0 and 1.")
    if df_cashflow is None or df_cashflow.empty:
        raise ValueError("Cash-flow dataset must not be empty.")

    df = df_cashflow.copy()

    # Support either raw transactions or already calculated net-flow data.
    if {"date", "transaction_type", "amount"}.issubset(df.columns):
        df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        if df["date"].isna().any() or not np.isfinite(df["amount"]).all():
            raise ValueError("Dates and amounts must contain valid finite values.")
        if (df["amount"] < 0).any():
            raise ValueError("Transaction amounts must be non-negative.")

        transaction_types = (
            df["transaction_type"].astype("string").str.strip().str.lower()
        )
        valid_types = {
            "inflow", "income", "credit", "receipt",
            "outflow", "expense", "debit", "payment",
        }
        if (
            transaction_types.isna().any()
            or not transaction_types.isin(valid_types).all()
        ):
            raise ValueError("Unknown or missing transaction types found.")

        df["transaction_type"] = transaction_types
        inflow_types = {"inflow", "income", "credit", "receipt"}
        df["net_flow"] = np.where(
            df["transaction_type"].isin(inflow_types),
            df["amount"],
            -df["amount"],
        )

    elif (
        {"net_flow"}.issubset(df.columns)
        and ({"date"}.issubset(df.columns) or {"trans_date"}.issubset(df.columns))
    ):
        date_col = "date" if "date" in df.columns else "trans_date"
        df["date"] = pd.to_datetime(df[date_col], errors="coerce", format="mixed")
        df["net_flow"] = pd.to_numeric(df["net_flow"], errors="coerce")

        if df["date"].isna().any() or not np.isfinite(df["net_flow"]).all():
            raise ValueError("Dates and net_flow must contain valid finite values.")

    else:
        raise ValueError(
            "Cash-flow data must contain either date/transaction_type/amount "
            "or date (or trans_date)/net_flow."
        )

    df = df.sort_values("date").reset_index(drop=True)

    # Aggregate all transactions on each calendar day.
    df["date"] = df["date"].dt.normalize()
    df = (
        df.groupby("date", as_index=False)["net_flow"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Finite transaction rows can still overflow when summed per day.
    if not np.isfinite(df["net_flow"].to_numpy(dtype=float)).all():
        raise ValueError(
            "Daily cash-flow aggregation produced non-finite values; "
            "check for numeric overflow."
        )

    date_gaps = df["date"].diff().dropna()
    if (date_gaps > pd.Timedelta(days=1)).any():
        raise ValueError(
            "Cash-flow evaluation requires consecutive calendar days; "
            "missing dates must be resolved before next-day forecasting."
        )

    # Predict the next day's net flow using past-only features.
    df["target_next_flow"] = df["net_flow"].shift(-1)
    df["lag_1d"] = df["net_flow"]
    df["lag_7d"] = df["net_flow"].shift(7)
    df["rolling_mean_7d"] = df["net_flow"].rolling(window=7, min_periods=1).mean()
    df["rolling_median_7d"] = df["net_flow"].rolling(window=7, min_periods=1).median()

    # Remove rows without a next-day target or required lag features.
    df_clean = df.dropna().reset_index(drop=True)

    if len(df_clean) < 30:
        raise ValueError("Cash-flow evaluation requires at least 30 valid samples.")

    # Chronological Split
    split_idx = int(len(df_clean) * train_ratio)

    if split_idx < 2 or (len(df_clean) - split_idx) < 2:
        raise ValueError(
            "Temporal evaluation requires at least 2 samples in both "
            "the training and test sets. Adjust train_ratio or provide "
            "more valid samples."
        )

    train = df_clean.iloc[:split_idx]
    test = df_clean.iloc[split_idx:]

    features = ['lag_1d', 'lag_7d', 'rolling_mean_7d', 'rolling_median_7d']
    X_train, y_train = train[features], train['target_next_flow']
    X_test, y_test = test[features], test['target_next_flow']

    # 1. Naive Baseline: Last observed net flow
    y_pred_baseline = X_test['lag_1d']
    baseline_mae = mean_absolute_error(y_test, y_pred_baseline)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, y_pred_baseline))

    # 2. Noise-Robust Random Forest
    rf_model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)  # Limited depth avoids noise overfitting
    rf_model.fit(X_train, y_train)
    y_pred_rf = rf_model.predict(X_test)

    rf_mae = mean_absolute_error(y_test, y_pred_rf)
    rf_rmse = np.sqrt(mean_squared_error(y_test, y_pred_rf))

    return {
        "level": "Level 1: Temporal Validation",
        "task": "Cash Flow Forecasting",
        "train_period": f"{train['date'].min().strftime('%Y-%m-%d')} to {train['date'].max().strftime('%Y-%m-%d')}",
        "test_period": f"{test['date'].min().strftime('%Y-%m-%d')} to {test['date'].max().strftime('%Y-%m-%d')}",
        "train_samples": len(train),
        "test_samples": len(test),
        "baseline_metrics": {"MAE": float(np.round(baseline_mae, 2)), "RMSE": float(np.round(baseline_rmse, 2))},
        "ml_model_metrics": {"MAE": float(np.round(rf_mae, 2)), "RMSE": float(np.round(rf_rmse, 2))},
        "improvement_pct": (None if baseline_mae == 0 else float(np.round(((baseline_mae - rf_mae) / baseline_mae) * 100, 2))),
        "leakage_safeguards": "Strict Temporal Chronological Split + Rolling Median Robust Aggregations Enabled"
    }



def evaluate_rolling_origin_cashflow(
    df_cashflow: pd.DataFrame,
    n_splits: int = 3,
    min_train_samples: int = 30,
) -> Dict[str, Any]:
    """
    Expanding-window rolling-origin validation for next-day cash-flow forecasts.
    Each fold trains only on earlier observations and evaluates on a later block.
    """
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2.")
    if min_train_samples < 10:
        raise ValueError("min_train_samples must be at least 10.")

    # Reuse the same input normalization and daily aggregation as the main evaluator.
    if df_cashflow is None or df_cashflow.empty:
        raise ValueError("Cash-flow dataset must not be empty.")

    df = df_cashflow.copy()

    if {"date", "transaction_type", "amount"}.issubset(df.columns):
        df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        types = df["transaction_type"].astype("string").str.strip().str.lower()
        inflows = {"inflow", "income", "credit", "receipt"}
        outflows = {"outflow", "expense", "debit", "payment"}
        valid_types = inflows | outflows

        if (
            df["date"].isna().any()
            or not np.isfinite(df["amount"]).all()
            or (df["amount"] < 0).any()
            or types.isna().any()
            or not types.isin(valid_types).all()
        ):
            raise ValueError("Invalid dates, amounts, or transaction types.")

        df["net_flow"] = np.where(types.isin(inflows), df["amount"], -df["amount"])

    elif "net_flow" in df.columns and (
        "date" in df.columns or "trans_date" in df.columns
    ):
        date_col = "date" if "date" in df.columns else "trans_date"
        df["date"] = pd.to_datetime(df[date_col], errors="coerce", format="mixed")
        df["net_flow"] = pd.to_numeric(df["net_flow"], errors="coerce")
        if df["date"].isna().any() or not np.isfinite(df["net_flow"]).all():
            raise ValueError("Dates and net_flow must contain valid finite values.")
    else:
        raise ValueError(
            "Expected date/transaction_type/amount or date (or trans_date)/net_flow."
        )

    df["date"] = df["date"].dt.normalize()
    daily = (
        df.groupby("date", as_index=False)["net_flow"]
        .sum()
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Finite transaction rows can still overflow when summed per day.
    if not np.isfinite(daily["net_flow"].to_numpy(dtype=float)).all():
        raise ValueError(
            "Daily cash-flow aggregation produced non-finite values; "
            "check for numeric overflow."
        )

    date_gaps = daily["date"].diff().dropna()
    if (date_gaps > pd.Timedelta(days=1)).any():
        raise ValueError(
            "Cash-flow evaluation requires consecutive calendar days; "
            "missing dates must be resolved before next-day forecasting."
        )

    daily["target_next_flow"] = daily["net_flow"].shift(-1)
    daily["lag_1d"] = daily["net_flow"]
    daily["lag_7d"] = daily["net_flow"].shift(7)
    daily["rolling_mean_7d"] = daily["net_flow"].rolling(7, min_periods=1).mean()
    daily["rolling_median_7d"] = daily["net_flow"].rolling(7, min_periods=1).median()
    clean = daily.dropna().reset_index(drop=True)

    features = ["lag_1d", "lag_7d", "rolling_mean_7d", "rolling_median_7d"]
    if len(clean) < min_train_samples + n_splits * 2:
        raise ValueError(
            f"Need at least {min_train_samples + n_splits * 2} valid samples "
            "for the requested rolling-origin evaluation."
        )

    # Keep the folds chronological; each later fold has a larger training window.
    test_size = (len(clean) - min_train_samples) // n_splits
    if test_size < 2:
        raise ValueError("Each rolling-origin test fold must have at least 2 samples.")

    fold_results = []
    for fold in range(n_splits):
        train_end = min_train_samples + fold * test_size
        test_end = (
            len(clean)
            if fold == n_splits - 1
            else min(train_end + test_size, len(clean))
        )

        train = clean.iloc[:train_end]
        test = clean.iloc[train_end:test_end]
        if len(test) < 2:
            continue

        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=5,
            random_state=42,
        )
        model.fit(train[features], train["target_next_flow"])
        predictions = model.predict(test[features])
        baseline = test["lag_1d"]
        actual = test["target_next_flow"]

        baseline_mae = mean_absolute_error(actual, baseline)
        model_mae = mean_absolute_error(actual, predictions)

        fold_results.append({
            "fold": fold + 1,
            "train_samples": len(train),
            "test_samples": len(test),
            "train_end": train["date"].max().strftime("%Y-%m-%d"),
            "test_start": test["date"].min().strftime("%Y-%m-%d"),
            "test_end": test["date"].max().strftime("%Y-%m-%d"),
            "baseline_MAE": float(np.round(baseline_mae, 2)),
            "model_MAE": float(np.round(model_mae, 2)),
            "improvement_pct": (
                None if baseline_mae == 0
                else float(np.round((baseline_mae - model_mae) / baseline_mae * 100, 2))
            ),
        })

    if len(fold_results) < 2:
        raise ValueError("Could not create at least two valid chronological folds.")

    return {
        "task": "Cash Flow Forecasting",
        "validation": "Expanding-window rolling-origin",
        "folds": fold_results,
        "mean_baseline_MAE": float(np.round(
            np.mean([row["baseline_MAE"] for row in fold_results]), 2
        )),
        "mean_model_MAE": float(np.round(
            np.mean([row["model_MAE"] for row in fold_results]), 2
        )),
        "folds_model_beats_baseline": sum(
            row["model_MAE"] < row["baseline_MAE"] for row in fold_results
        ),
        "warning": "Validation on this dataset alone does not establish real-world SME performance.",
    }

def evaluate_invoice_late_payment(
    df_invoices: pd.DataFrame,
    train_ratio: float = 0.8
) -> Dict[str, Any]:
    """
    Evaluate invoice late-payment classification after validating
    the feature schema and target-label consistency.
    """
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1.")

    if not isinstance(df_invoices, pd.DataFrame) or df_invoices.empty:
        raise ValueError("Invoice data must be a non-empty DataFrame.")

    df = df_invoices.copy()
    features = ["invoice_amount", "payment_terms_days"]

    missing_features = [col for col in features if col not in df.columns]
    if missing_features:
        raise ValueError(
            f"Missing required invoice feature columns: {missing_features}"
        )

    if "is_late" not in df.columns:
        if "days_late" not in df.columns:
            raise ValueError(
                "Invoice data must contain is_late or days_late."
            )
        days_late = pd.to_numeric(df["days_late"], errors="coerce")
        if days_late.isna().any() or not np.isfinite(days_late).all():
            raise ValueError("days_late must contain finite numeric values.")
        df["is_late"] = (days_late > 0).astype(int)

    if df["is_late"].isna().any():
        raise ValueError("is_late must not contain missing values.")

    if not df["is_late"].isin([0, 1]).all():
        raise ValueError("is_late labels must be binary values 0 or 1.")

    if "days_late" in df.columns:
        days_late = pd.to_numeric(df["days_late"], errors="coerce")
        if days_late.isna().any() or not np.isfinite(days_late).all():
            raise ValueError("days_late must contain finite numeric values.")
        if (days_late < 0).any():
            raise ValueError("days_late cannot be negative.")
        expected_labels = (days_late > 0).astype(int)
        if not (expected_labels.to_numpy() == df["is_late"].to_numpy()).all():
            raise ValueError(
                "Inconsistent target labels: is_late does not match "
                "days_late > 0. Verify the official label definition "
                "before evaluating this dataset."
            )

    for col in features:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any() or not np.isfinite(df[col]).all():
            raise ValueError(f"{col} must contain finite numeric values.")

    if (df["invoice_amount"] < 0).any():
        raise ValueError("invoice_amount cannot be negative.")
    if (df["payment_terms_days"] <= 0).any():
        raise ValueError("payment_terms_days must be positive.")

    if len(df) < 5:
        raise ValueError("At least 5 invoice rows are required.")

    X = df[features]
    y = df["is_late"].astype(int)

    split_idx = int(len(df) * train_ratio)
    if split_idx < 2 or len(df) - split_idx < 2:
        raise ValueError("Train and test splits must each contain at least 2 rows.")

    X_train, y_train = X.iloc[:split_idx], y.iloc[:split_idx]
    X_test, y_test = X.iloc[split_idx:], y.iloc[split_idx:]

    if y_train.nunique() < 2:
        raise ValueError("Training data must contain both target classes.")
    if y_test.nunique() < 2:
        raise ValueError("Test data must contain both target classes.")

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=5,
        random_state=42
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    prec_curve, rec_curve, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = auc(rec_curve, prec_curve)

    return {
        "level": "Level 1: Classification Evaluation",
        "task": "Invoice Late Payment Prediction",
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "metrics": {
            "Precision": float(np.round(precision, 2)),
            "Recall": float(np.round(recall, 2)),
            "PR_AUC": float(np.round(pr_auc, 2))
        }
    }


if __name__ == "__main__":
    from pathlib import Path

    print("--- Running Level 1 Temporal Validation Suite ---")

    # Cash-flow evaluation using the project's validated data loader.
    try:
        df_cf = load_sme_data()
        cf_results = evaluate_temporal_cashflow_forecasting(df_cf)
        print("\n[Cash Flow Forecasting Results]")
        print(cf_results)
    except (ValueError, FileNotFoundError) as exc:
        print(f"\n[Cash Flow Evaluation NOT completed] {exc}")

    # Invoice evaluation. Preserve source labels and report validation errors.
    invoice_path = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "raw"
        / "barnet_invoices.csv"
    )

    try:
        df_inv = pd.read_csv(invoice_path)
        inv_results = evaluate_invoice_late_payment(df_inv)
        print("\n[Invoice Late Payment Results]")
        print(inv_results)
    except (ValueError, FileNotFoundError, OSError, pd.errors.ParserError) as exc:
        print(f"\n[Invoice Evaluation NOT completed] {exc}")
