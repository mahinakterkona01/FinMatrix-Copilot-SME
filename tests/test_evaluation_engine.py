import numpy as np
import pandas as pd
import pytest

from src.evaluation_engine import evaluate_temporal_cashflow_forecasting


def make_cashflow_data(days=40, amount=100.0, transaction_type="inflow"):
    return pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=days, freq="D"),
        "transaction_type": [transaction_type] * days,
        "amount": [amount] * days,
    })


def test_evaluation_returns_metrics_and_chronological_split():
    df = make_cashflow_data()
    result = evaluate_temporal_cashflow_forecasting(df)

    assert result["train_samples"] > 0
    assert result["test_samples"] > 0
    assert result["train_period"] < result["test_period"]
    assert np.isfinite(result["baseline_metrics"]["MAE"])
    assert np.isfinite(result["ml_model_metrics"]["MAE"])


@pytest.mark.parametrize("train_ratio", [0, 1, -0.1, 1.1])
def test_evaluation_rejects_invalid_train_ratio(train_ratio):
    with pytest.raises(ValueError):
        evaluate_temporal_cashflow_forecasting(
            make_cashflow_data(), train_ratio=train_ratio
        )


def test_evaluation_rejects_empty_data():
    with pytest.raises(ValueError):
        evaluate_temporal_cashflow_forecasting(pd.DataFrame())


def test_evaluation_rejects_unknown_transaction_type():
    df = make_cashflow_data()
    df.loc[0, "transaction_type"] = "unknown"

    with pytest.raises(ValueError):
        evaluate_temporal_cashflow_forecasting(df)


def test_evaluation_rejects_invalid_date():
    df = make_cashflow_data()
    df["date"] = df["date"].astype(str)
    df.loc[0, "date"] = "not-a-date"

    with pytest.raises(ValueError):
        evaluate_temporal_cashflow_forecasting(df)


def test_evaluation_handles_inflow_aliases():
    for transaction_type in ["inflow", "income", "credit", "receipt"]:
        df = make_cashflow_data(transaction_type=transaction_type)
        result = evaluate_temporal_cashflow_forecasting(df)
        assert np.isfinite(result["ml_model_metrics"]["MAE"])


def test_evaluation_handles_outflow_aliases():
    for transaction_type in ["outflow", "expense", "debit", "payment"]:
        df = make_cashflow_data(transaction_type=transaction_type)
        result = evaluate_temporal_cashflow_forecasting(df)
        assert np.isfinite(result["ml_model_metrics"]["MAE"])


def test_zero_baseline_mae_returns_none_improvement():
    df = make_cashflow_data(days=40, amount=100.0, transaction_type="inflow")
    result = evaluate_temporal_cashflow_forecasting(df)

    assert result["baseline_metrics"]["MAE"] == 0.0
    assert result["improvement_pct"] is None


def test_evaluation_rejects_insufficient_samples():
    df = make_cashflow_data(days=18)

    with pytest.raises(ValueError, match="at least 30 valid samples"):
        evaluate_temporal_cashflow_forecasting(df)


def test_evaluation_rejects_too_small_test_split():
    df = make_cashflow_data(days=40)

    with pytest.raises(ValueError, match="at least 2 samples"):
        evaluate_temporal_cashflow_forecasting(df, train_ratio=0.99)

from src.evaluation_engine import evaluate_temporal_cashflow_forecasting


def test_evaluation_aggregates_multiple_transactions_per_day():
    daily_dates = pd.date_range("2026-01-01", periods=40, freq="D")
    rows = []

    for date in daily_dates:
        rows.append({
            "date": date,
            "transaction_type": "inflow",
            "amount": 200.0,
        })
        rows.append({
            "date": date,
            "transaction_type": "outflow",
            "amount": 50.0,
        })

    df = pd.DataFrame(rows)
    result = evaluate_temporal_cashflow_forecasting(df)

    # Each day has two transactions, but the evaluation should use
    # one daily net-flow observation: 200 - 50 = 150.
    assert result["train_samples"] + result["test_samples"] == 32
    assert result["baseline_metrics"]["MAE"] == 0.0

from src.evaluation_engine import evaluate_invoice_late_payment


def make_invoice_data(rows=50):
    return pd.DataFrame({
        "invoice_amount": np.linspace(100, 5000, rows),
        "payment_terms_days": [30] * rows,
        "is_late": [0, 1] * (rows // 2) + ([0] if rows % 2 else []),
    })


def test_invoice_evaluation_returns_metrics():
    result = evaluate_invoice_late_payment(make_invoice_data())

    assert result["train_samples"] == 40
    assert result["test_samples"] == 10
    assert set(result["metrics"]) == {"Precision", "Recall", "PR_AUC"}


def test_invoice_evaluation_rejects_missing_required_column():
    df = make_invoice_data().drop(columns=["invoice_amount"])

    with pytest.raises(ValueError):
        evaluate_invoice_late_payment(df)


def test_invoice_evaluation_rejects_invalid_target_labels():
    df = make_invoice_data()
    df.loc[0, "is_late"] = 2

    with pytest.raises(ValueError):
        evaluate_invoice_late_payment(df)


def test_invoice_evaluation_rejects_inconsistent_late_payment_labels():
    df = make_invoice_data()
    df["days_late"] = np.where(df["is_late"] == 1, 5, 0)
    df.loc[0, "days_late"] = 5
    df.loc[0, "is_late"] = 0

    with pytest.raises(ValueError):
        evaluate_invoice_late_payment(df)

def test_evaluation_accepts_cleaned_sme_loader_schema():
    from src.data_loader import load_sme_data

    df = load_sme_data()
    assert {"trans_date", "net_flow"}.issubset(df.columns)

    result = evaluate_temporal_cashflow_forecasting(df)

    assert result["task"] == "Cash Flow Forecasting"
    assert result["train_samples"] > 0
    assert result["test_samples"] > 0
    assert "MAE" in result["ml_model_metrics"]

def test_rolling_origin_cashflow_returns_chronological_folds():
    from src.data_loader import load_sme_data
    from src.evaluation_engine import evaluate_rolling_origin_cashflow

    df = load_sme_data()
    result = evaluate_rolling_origin_cashflow(df, n_splits=3, min_train_samples=30)

    assert result["validation"] == "Expanding-window rolling-origin"
    assert len(result["folds"]) == 3
    assert result["mean_baseline_MAE"] >= 0
    assert result["mean_model_MAE"] >= 0

    previous_train_samples = 0
    for fold in result["folds"]:
        assert fold["train_samples"] > previous_train_samples
        assert fold["test_samples"] >= 2
        assert fold["train_end"] < fold["test_start"]
        previous_train_samples = fold["train_samples"]


def test_rolling_origin_cashflow_rejects_too_few_splits():
    import pytest
    from src.data_loader import load_sme_data
    from src.evaluation_engine import evaluate_rolling_origin_cashflow

    with pytest.raises(ValueError, match="n_splits"):
        evaluate_rolling_origin_cashflow(load_sme_data(), n_splits=1)


def test_rolling_origin_cashflow_rejects_insufficient_data():
    import pytest
    import pandas as pd
    from src.evaluation_engine import evaluate_rolling_origin_cashflow

    df = pd.DataFrame({
        "trans_date": pd.date_range("2026-01-01", periods=20, freq="D"),
        "net_flow": range(20),
    })

    with pytest.raises(ValueError, match="Need at least"):
        evaluate_rolling_origin_cashflow(df, n_splits=3, min_train_samples=30)


def test_invoice_evaluation_rejects_negative_days_late():
    df = make_invoice_data()
    df["days_late"] = np.where(df["is_late"] == 1, 5, 0)
    df.loc[0, "days_late"] = -1
    df.loc[0, "is_late"] = 0

    with pytest.raises(ValueError, match="days_late cannot be negative"):
        evaluate_invoice_late_payment(df)


def test_invoice_evaluation_rejects_non_numeric_days_late():
    df = make_invoice_data()
    df["days_late"] = np.where(df["is_late"] == 1, 5, 0)
    df["days_late"] = df["days_late"].astype(object)
    df.loc[0, "days_late"] = "unknown"

    with pytest.raises(ValueError, match="days_late must contain finite numeric values"):
        evaluate_invoice_late_payment(df)


def test_rolling_origin_cashflow_rejects_missing_calendar_dates():
    from src.evaluation_engine import evaluate_rolling_origin_cashflow

    dates = pd.date_range("2026-01-01", periods=50, freq="D").delete(20)
    df = pd.DataFrame({
        "trans_date": dates,
        "net_flow": range(len(dates)),
    })

    with pytest.raises(ValueError, match="consecutive calendar days"):
        evaluate_rolling_origin_cashflow(
            df, n_splits=3, min_train_samples=30
        )

def test_daily_aggregation_overflow_is_rejected():
    import pandas as pd
    import pytest
    from src.evaluation_engine import evaluate_temporal_cashflow_forecasting

    dates = pd.date_range("2026-01-01", periods=40, freq="D")
    df = pd.DataFrame({
        "date": list(dates) * 2,
        "transaction_type": ["inflow"] * 80,
        "amount": [1e308] * 80,
    })

    with pytest.raises(ValueError, match="Daily cash-flow aggregation"):
        evaluate_temporal_cashflow_forecasting(df)


def test_rolling_origin_daily_aggregation_overflow_is_rejected():
    import pandas as pd
    import pytest
    from src.evaluation_engine import evaluate_rolling_origin_cashflow

    dates = pd.date_range("2026-01-01", periods=40, freq="D")
    df = pd.DataFrame({
        "date": list(dates) * 2,
        "transaction_type": ["inflow"] * 80,
        "amount": [1e308] * 80,
    })

    with pytest.raises(ValueError, match="Daily cash-flow aggregation"):
        evaluate_rolling_origin_cashflow(df)

