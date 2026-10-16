
import numpy as np
import pandas as pd
import pytest

from src.forecasting import CashFlowForecaster


def make_sample_data(days=60):
    """Create deterministic sample data for testing only."""
    dates = pd.date_range("2026-01-01", periods=days, freq="D")
    net_flow = [
        5000 + (i % 7) * 300 - (i % 5) * 100
        for i in range(days)
    ]

    return pd.DataFrame({
        "trans_date": dates,
        "net_flow": net_flow,
    })


def test_forecast_returns_expected_structure():
    df = make_sample_data()
    forecaster = CashFlowForecaster()

    result = forecaster.predict_next_days(df, days=7)

    assert len(result) == 7
    assert list(result.columns) == ["Date", "Predicted_Net_Flow"]
    assert pd.api.types.is_datetime64_any_dtype(result["Date"])
    assert np.isfinite(result["Predicted_Net_Flow"]).all()


def test_forecast_dates_follow_last_historical_date():
    df = make_sample_data()
    forecaster = CashFlowForecaster()

    result = forecaster.predict_next_days(df, days=5)

    expected_dates = pd.date_range(
        start=df["trans_date"].max() + pd.Timedelta(days=1),
        periods=5,
        freq="D",
    )

    assert list(result["Date"]) == list(expected_dates)


def test_forecast_rejects_insufficient_history():
    df = make_sample_data(days=10)
    forecaster = CashFlowForecaster()

    with pytest.raises(ValueError):
        forecaster.predict_next_days(df, days=7)


def test_forecast_rejects_missing_net_flow():
    df = make_sample_data().drop(columns=["net_flow"])
    forecaster = CashFlowForecaster()

    with pytest.raises((ValueError, KeyError)):
        forecaster.predict_next_days(df, days=7)


@pytest.mark.parametrize("days", [0, -1, -30])
def test_forecast_rejects_invalid_days(days):
    df = make_sample_data()
    forecaster = CashFlowForecaster()

    with pytest.raises(ValueError):
        forecaster.predict_next_days(df, days=days)


def test_forecast_rejects_missing_date_column():
    df = make_sample_data().drop(columns=["trans_date"])
    forecaster = CashFlowForecaster()

    with pytest.raises((ValueError, KeyError)):
        forecaster.predict_next_days(df, days=7)


def test_forecast_rejects_non_finite_net_flow():
    df = make_sample_data()
    df.loc[10, "net_flow"] = np.nan
    forecaster = CashFlowForecaster()

    with pytest.raises(ValueError):
        forecaster.predict_next_days(df, days=7)
