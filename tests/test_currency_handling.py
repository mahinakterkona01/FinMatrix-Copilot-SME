import pandas as pd
import pytest

from src.normalization import normalize_columns


@pytest.mark.parametrize(
    ("raw_amount", "expected"),
    [
        ("$1,250.50", 1250.50),
        ("৳1,250.50", 1250.50),
        ("€1,250.50", 1250.50),
        ("£1,250.50", 1250.50),
        ("¥1,250.50", 1250.50),
        ("1250.50", 1250.50),
    ],
)
def test_normalize_columns_parses_currency_formatted_amounts(
    raw_amount, expected
):
    df = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "amount": [raw_amount],
            "transaction_type": ["inflow"],
        }
    )

    result = normalize_columns(df)

    assert result.loc[0, "amount"] == pytest.approx(expected)
    assert result.loc[0, "inflow"] == pytest.approx(expected)
    assert result.loc[0, "outflow"] == pytest.approx(0.0)
    assert result.loc[0, "net_flow"] == pytest.approx(expected)


def test_normalize_columns_rejects_invalid_amount():
    df = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "amount": ["not-a-number"],
            "transaction_type": ["inflow"],
        }
    )

    with pytest.raises(ValueError, match="amount"):
        normalize_columns(df)


def test_normalize_columns_calculates_net_flow():
    df = pd.DataFrame(
        {
            "date": ["2026-01-01"],
            "inflow": ["$2,000.00"],
            "outflow": ["$500.00"],
        }
    )

    result = normalize_columns(df)

    assert result.loc[0, "inflow"] == pytest.approx(2000.0)
    assert result.loc[0, "outflow"] == pytest.approx(500.0)
    assert result.loc[0, "net_flow"] == pytest.approx(1500.0)


