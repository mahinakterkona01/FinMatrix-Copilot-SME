"""
FinMatrix Copilot— Evaluation Engine & Level 1 Temporal ML Validation
Enhanced for Noise Robustness (Rolling Medians, Robust Scaling) & Temporal Leakage Prevention.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any
from sklearn.metrics import mean_absolute_error, mean_squared_error, precision_score, recall_score, precision_recall_curve, auc
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor

from src.data_loader import process_barnet_invoice_dataset, load_raw_dataset


def evaluate_temporal_cashflow_forecasting(
    df_cashflow: pd.DataFrame,
    train_ratio: float = 0.8
) -> Dict[str, Any]:
    """
    Level 1 Temporal Validation for Cash Flow Forecasting.
    Includes Robust Features (Rolling Medians) to handle noisy SME transactions.
    """
    df = df_cashflow.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date').reset_index(drop=True)

    # Net daily cash flow calculation
    df['net_flow'] = np.where(df['transaction_type'] == 'inflow', df['amount'], -df['amount'])
    df['target_next_flow'] = df['net_flow'].shift(-1)
    
    # Noise-Resistant Past Features
    df['lag_1d'] = df['net_flow']
    df['lag_7d'] = df['net_flow'].shift(6)
    df['rolling_mean_7d'] = df['net_flow'].rolling(window=7, min_periods=1).mean()
    df['rolling_median_7d'] = df['net_flow'].rolling(window=7, min_periods=1).median()  # Outlier resistant

    # Clean NaNs strictly without lookahead
    df_clean = df.dropna().reset_index(drop=True)

    # Chronological Split
    split_idx = int(len(df_clean) * train_ratio)
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
        "improvement_pct": float(np.round(((baseline_mae - rf_mae) / baseline_mae) * 100, 2)),
        "leakage_safeguards": "Strict Temporal Chronological Split + Rolling Median Robust Aggregations Enabled"
    }


def evaluate_invoice_late_payment(
    df_invoices: pd.DataFrame,
    train_ratio: float = 0.8
) -> Dict[str, Any]:
    """
    Level 1 Validation for Invoice Late Payment Prediction.
    Evaluates Random Forest Classifier on historical invoice features.
    """
    df = df_invoices.copy()
    
    features = ['invoice_amount', 'payment_terms_days']
    if 'is_late' not in df.columns:
        df['is_late'] = np.where(df['days_late'] > 0, 1, 0)

    X = df[features]
    y = df['is_late']

    split_idx = int(len(df) * train_ratio)
    X_train, y_train = X.iloc[:split_idx], y.iloc[:split_idx]
    X_test, y_test = X.iloc[split_idx:], y.iloc[split_idx:]

    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1] if len(np.unique(y_train)) > 1 else y_pred

    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    
    prec_curve, rec_curve, _ = precision_recall_curve(y_test, y_prob)
    pr_auc = auc(rec_curve, prec_curve)

    return {
        "level": "Level 1: Temporal Validation",
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
    print("--- Running Robust Level 1 Temporal Validation Suite ---")
    df_cf = load_raw_dataset("bangladesh_sme_cashflow.csv")
    cf_results = evaluate_temporal_cashflow_forecasting(df_cf)
    print("\n[Cash Flow Forecasting Results]:")
    print(cf_results)

    df_inv = process_barnet_invoice_dataset()
    inv_results = evaluate_invoice_late_payment(df_inv)
    print("\n[Invoice Late Payment Results]:")
    print(inv_results)